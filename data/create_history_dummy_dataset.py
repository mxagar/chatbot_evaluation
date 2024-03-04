"""This module creates a dummy dataset
following the "history" format;
it's purpose is for temporary testing.

Usage:

    python ./create_history_dummy_dataset.py

Author: Mikel Sagardia
Date: 2024-03-01
"""
import pandas as pd
from datetime import datetime, timedelta

# Define the structure of the dataset
data = {
    "id": [1, 2, 3, 4, 5],
    "timestamp": [(datetime.now() - timedelta(days=i)).strftime('%d.%m.%Y, %H:%M:%S.%f') for i in range(5)],
    "history": [
        "[{'user': 'How do I make a chocolate cake?', 'bot': 'Mix flour, sugar, cocoa powder, baking powder, and eggs. Bake at 350°F for 30 minutes.'}]",
        "[{'user': 'What ingredients do I need for spaghetti carbonara?', 'bot': 'You need spaghetti, eggs, pancetta, parmesan cheese, and black pepper.'}]",
        "[{'user': 'How long does it take to cook a medium-rare steak?', 'bot': 'Cook the steak for about 4-5 minutes on each side for medium-rare.'}]",
        "[{'user': 'Can I substitute almond milk for regular milk in recipes?', 'bot': 'Yes, almond milk can typically be used as a 1:1 substitute for regular milk.'}, {'user': 'Even in baking?', 'bot': 'Yes, but the texture and taste might slightly differ.'}, {'user': 'Thank you!', 'bot': 'You\\'re welcome!'}]",
        "[{'user': 'What is the best way to store fresh herbs?', 'bot': 'Wrap them in a damp paper towel and store them in the fridge.'}, {'user': 'Does this work for all herbs?', 'bot': 'It works best for herbs like parsley, cilantro, and basil.'}, {'user': 'Great, thanks!', 'bot': 'Glad to help!'}]"
    ],
    "rating": [5, 4, 4, 5, 3],
    "message": [
        "The answer was very helpful.",
        "Good response, but a bit more detail would be great.",
        "Satisfied with the answer.",
        "Very informative and helpful response.",
        "Answer was okay, could use more specifics."
    ]
}

# Create a DataFrame and save it as a CSV
df = pd.DataFrame(data)
file_path = "chat_history_dummy.csv"
df.to_csv(file_path, index=False)
