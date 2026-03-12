import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta

# 1. Generate Complaints Dataset (200 rows)
def generate_complaints():
    categories = ['Electrical', 'Plumbing', 'Elevator', 'Security', 'Cleanliness', 'Carpentry']
    locations = ['Block A', 'Block B', 'Block C', 'Clubhouse', 'Basement Parking', 'Main Gate']
    priorities = ['Low', 'Medium', 'High', 'Critical']
    statuses = ['Open', 'Assigned', 'In Progress', 'Resolved', 'Closed']
    
    descriptions = {
        'Electrical': ['Power cut in apartment', 'Street light not working', 'Short circuit in MCB', 'Corridor lights flickering', 'No power in Block B', 'Switchboard sparking'],
        'Plumbing': ['Water leakage in bathroom', 'No water supply', 'Drainage blocked', 'Kitchen sink pipe leaking', 'Overhead tank overflowing', 'Dripping tap in washroom'],
        'Elevator': ['Lift stuck between floors', 'Lift buttons not responding', 'Lift making strange noise', 'Elevator door not closing', 'Lift fan not working', 'Elevator display broken'],
        'Security': ['Unknown person loitering', 'Security guard sleeping on duty', 'Boom barrier not opening', 'CCTV camera broken', 'Main gate unattended', 'Bypass entry detected'],
        'Cleanliness': ['Garbage not collected', 'Staircase is very dirty', 'Corridor sweeping missed', 'Foul smell near dustbin', 'Dead rat in parking', 'Clubhouse washroom unclean'],
        'Carpentry': ['Door hinge broken', 'Window sliding track jammed', 'Cupboard handle loose', 'Main door lock stuck', 'Wooden flooring damage', 'Balcony door not closing']
    }

    data = []
    base_date = datetime.now() - timedelta(days=90)
    
    for i in range(1, 251): # Generate 250 rows to be safe
        category = random.choice(categories)
        desc = random.choice(descriptions[category])
        
        # Add some variation to description to test similarity
        if random.random() > 0.7:
             desc = desc.lower() + " please fix ASAP"
        elif random.random() > 0.5:
             desc = "Issue: " + desc

        record = {
            'complaint_id': f"CMP{str(i).zfill(4)}",
            'resident_id': f"RES{random.randint(100, 999)}",
            'description': desc,
            'location': random.choice(locations),
            'category': category,
            'priority': random.choice(priorities),
            'status': random.choice(statuses),
            'timestamp': (base_date + timedelta(days=random.randint(0, 89), hours=random.randint(0, 23), minutes=random.randint(0,59))).strftime('%Y-%m-%d %H:%M:%S'),
            'assigned_staff': f"TECH{random.randint(10, 50)}" if random.random() > 0.2 else None
        }
        data.append(record)
    
    df = pd.DataFrame(data)
    df.to_csv('complaints.csv', index=False)
    print("complaints.csv generated with", len(df), "rows.")

# 2. Generate Maintenance Logs Dataset (200 rows)
def generate_maintenance_logs():
    assets = ['Lift 1A', 'Lift 1B', 'Water Pump Main', 'Transformer Block A', 'DG Set 1', 'Swimming Pool Filter', 'STP Motor']
    actions = ['Routine Service', 'Part Replacement', 'Emergency Repair', 'Oil Change', 'Belt Alignment', 'Sensor Calibration']
    
    data = []
    base_date = datetime.now() - timedelta(days=365)
    
    for i in range(1, 221):
        record = {
            'log_id': f"LOG{str(i).zfill(4)}",
            'asset_name': random.choice(assets),
            'maintenance_type': 'Preventive' if random.random() > 0.4 else 'Corrective',
            'action_taken': random.choice(actions),
            'cost': round(random.uniform(500, 15000), 2),
            'date': (base_date + timedelta(days=random.randint(0, 360))).strftime('%Y-%m-%d'),
            'downtime_hours': round(random.uniform(0.5, 24.0), 1),
            'technician_id': f"TECH{random.randint(10, 50)}"
        }
        data.append(record)
        
    df = pd.DataFrame(data)
    # Sort by date
    df = df.sort_values(by='date')
    df.to_csv('maintenance_logs.csv', index=False)
    print("maintenance_logs.csv generated with", len(df), "rows.")

# 3. Generate Feedback Dataset (200 rows)
def generate_feedback():
    sentiments = ['Positive', 'Neutral', 'Negative']
    comments_pos = ['Quick resolution, thanks!', 'Very polite staff.', 'Excellent work.', 'Issue fixed permanently.', 'Satisfied with service.']
    comments_neu = ['Okay work.', 'Took some time but fixed.', 'Average service.', 'Could be better.', 'Fixed for now.']
    comments_neg = ['Terrible service.', 'Still not working.', 'Staff was rude.', 'Took 3 days to come.', 'Unprofessional.', 'Waste of time.']
    
    data = []
    for i in range(1, 211):
        score = random.randint(1, 5)
        if score >= 4:
            sentiment = 'Positive'
            comment = random.choice(comments_pos)
        elif score == 3:
            sentiment = 'Neutral'
            comment = random.choice(comments_neu)
        else:
            sentiment = 'Negative'
            comment = random.choice(comments_neg)
            
        record = {
            'feedback_id': f"FB{str(i).zfill(4)}",
            'complaint_id': f"CMP{random.randint(1, 250):04d}",
            'resident_id': f"RES{random.randint(100, 999)}",
            'rating': score,
            'comment': comment,
            'sentiment_label': sentiment
        }
        data.append(record)
        
    df = pd.DataFrame(data)
    df.to_csv('feedback.csv', index=False)
    print("feedback.csv generated with", len(df), "rows.")

if __name__ == "__main__":
    generate_complaints()
    generate_maintenance_logs()
    generate_feedback()
