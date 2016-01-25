import datetime
import time
import requests
import json
import pandas as pd
import numpy as np
from bs4 import BeautifulSoup
from IPython.display import clear_output

def get_athlete_performances(athlete_links):
    
    athlete_performances = {}

    for i, athlete_link in enumerate(athlete_links):
        # Get athlete pages 
        lname, fname = athlete_link.text.split(', ')
        print 'Getting perfomance information for '+fname+' '+lname+'.'
        pct_done = (float(i) / float(len(athlete_links))) * 100.
        print str(pct_done)+'% done with entire team.'
        clear_output(wait=True)
        athlete_page_url = athlete_link.attrs['href']
        athlete_page = BeautifulSoup(requests.get(athlete_page_url).text)
        tables = athlete_page.select('div.container')[1].select('table')

        if len(tables) > 1:
            performance_table = tables[1].find_all('tr')
            performance_data = []
            for performance in performance_table[1:]:
                performance_data.append([td.text.replace('\n','').replace('\t','').replace(' ','') for td in performance.find_all('td')])

            performance_df = pd.DataFrame(performance_data)
            performance_df.columns = [td.text.replace('\n','').replace(' ','') for td in performance_table[0].find_all('th')]
            performance_df['Time/Mark'] = performance_df['Time/Mark'].apply(fix_nt)
            performance_df['Event Type'] = performance_df['Time/Mark'].apply(lambda m: 'Field' if 'm' in m or not('.' in m) else 'Track')
            performance_df['Time/Mark'] = performance_df['Time/Mark'].apply(lambda m: float(m.split('m')[0]) if 'm' in m else get_timedelta(m))

            events = {event: performance_df[performance_df.Event == event] for event in performance_df.Event.unique()}

            top_performances = {}
            for e in events: 
                performances = events[e]['Time/Mark']
                event_type = events[e]['Event Type'].values[0]
                if event_type == 'Field':
                    top_performances[e] = performances.max()
                else:
                    top_performances[e] = performances.min()

            athlete_performances[lname+'_'+fname] = top_performances

        time.sleep(1)
    
    return athlete_performances 

def get_team_performances(team_ids):
    
    team_performances = {}

    for team_id in team_ids: 

        # Get the url for the team page 
        team_url = 'https://www.directathletics.com/team.html?team_hnd='+str(team_id)+'&sport=track&year=max'

        # Get team page
        team_page = BeautifulSoup(requests.get(team_url).text)

        # Get team name
        team_name = team_page.select('span.title_text')[0].text.replace(' ','')

        print team_name

        # Get team roster
        athlete_links = team_page.select('div.container')[1].table.find_all('table')[1].find_all('a')

        # Get best performances for each athlete on the team 
        team_performances[team_name] = get_athlete_performances(athlete_links)
    
    return team_performances


#======================== Helpers ==============================

def get_timedelta(time):
    minutes = 0
    if len(time.split(':')) > 1:
        minutes, seconds = [float(t) for t in time.split(':')]
    else:
        try:
            seconds = float(time)
        except ValueError:
            seconds = 1000 * 1000
        
    return datetime.timedelta(minutes=minutes, seconds=seconds)

def fix_nt(mark):
    if 'NT' in mark:
        return '1000:00.00'
    elif 'NH' in mark or 'ND' in mark:
        return '0m'
    elif not('NH' in mark) and 'H' in mark:
        return '1000:00.00'
    else:
        return mark
    
def save_performancs(team_performances, file_name='team_performances.json'):
    tp = team_performances

    for team in tp:
        for athlete in tp[team]:
            for event in tp[team][athlete]:
                mark = tp[team][athlete][event]
                if not type(mark) == float:
                    tp[team][athlete][event] = str(mark)

    with open(filen_name,'w') as f:
        json.dump(tp, f)        