import pandas as pd
import json
import datetime

def get_team_scores(teams, events, top_marks, scoring_rubric={0:10,1:8,2:6,3:4,4:2,5:1} ):
    
    team_scores = {school_name: {event: 0 for event in events} for school_name in teams}
    for team in team_scores:
        team_scores[team]['*Total*'] = 0

    for event_name in events:
        for i, (mark, athlete_name, school_name) in top_marks[event_name].iterrows():
            if i < len(scoring_rubric):
                points = scoring_rubric[i]
                team_scores[school_name][event_name] += points
                team_scores[school_name]['*Total*'] += points

    return pd.DataFrame(team_scores)
    
def get_top_marks(team_performances, limit=10):
    top_marks = {}

    for team_name in team_performances:
        team = team_performances[team_name]
        for athlete_name in team:
            athlete_performances = team[athlete_name]
            for event_name in athlete_performances:
                mark = athlete_performances[event_name]
                performance_info = (mark, athlete_name, team_name)
                if not(event_name in top_marks):
                    top_marks[event_name] = [performance_info]
                elif type(mark) == type(top_marks[event_name][-1][0]):
                    top_marks[event_name].append(performance_info)

    for event_name in top_marks:
        
        is_field_event = type(top_marks[event_name][0][0]) == float

        if is_field_event:
            top_marks[event_name] = sorted(top_marks[event_name], key=lambda p: p[0])[::-1][:limit]
        else:
            top_marks[event_name] = sorted(top_marks[event_name], key=lambda p: p[0])[:limit]

        top_marks[event_name] = pd.DataFrame(top_marks[event_name], columns= ['Time/Mark','Athlete','School'])
        
    return top_marks

def open_performances(file_name):
    with open(file_name, 'r') as f:
        tp = json.load(f)
    
    for team in tp:
        for athlete in tp[team]:
            for event in tp[team][athlete]:
                mark = tp[team][athlete][event]
                if not(type(mark) == float) and ':' in mark:
                    try:
                        days, time = mark.split(' days ')
                        hours, minutes, seconds = time.split(':')
                        tp[team][athlete][event] = datetime.timedelta(hours=int(hours), minutes=int(minutes), seconds=float(seconds))
                    except ValueError:
                        try:
                            hours, minutes, seconds = mark.split(':')
                            tp[team][athlete][event] = datetime.timedelta(hours=int(hours), minutes=int(minutes), seconds=float(seconds))
                        except ValueError:
                            print 'Could not process information on '+athlete+' from '+team+'.'
    return tp