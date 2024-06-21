# -*- coding: utf-8 -*-
"""LLM_FineTuned.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1qVfplxbR-_5eZHMd7ePsdM0LpwhhhMtt
"""

!pip install langchain
!pip install langchain_openai
!pip install openai

import pandas as pd

df = pd.read_csv("hf://datasets/Kaludi/Customer-Support-Responses/Customer-Support.csv")
df.head()

"""Removed all analysis on preprocessing as the data is limited with minimal/no processing required."""

records = []
for index, row in df.iterrows():
    messages = [
        {"role": "user", "content": f"{row['query']} ->"},
        {"role": "assistant", "content": f"{row['response']} \n"}
    ]
    record = {"messages": messages}
    records.append(record)
records

import json

training_file_name = "training_data.jsonl"
validation_file_name = "validation_data.jsonl"

def prepare_data(dictionary_data, final_file_name):
    with open(final_file_name, 'w') as outfile:
        for entry in dictionary_data:
            json.dump(entry, outfile)
            outfile.write('\n')

training_data = records[:60]
validation_data = records[60:]

prepare_data(training_data, "training_data.jsonl")
prepare_data(validation_data, "validation_data.jsonl")

import openai
from openai import OpenAI
from google.colab import userdata as ud

API_KEY = ud.get('OpenAI_API') # your api key in secret with name

client = OpenAI(api_key=API_KEY)

train_file = client.files.create(
    file=open('training_data.jsonl', 'rb'),
    purpose='fine-tune'
)
test_file = client.files.create(
    file=open('validation_data.jsonl', 'rb'),
    purpose='fine-tune'
)

# Fine-tune the model
fine_tune = client.fine_tuning.jobs.create(
                                  model="gpt-3.5-turbo",
                                  training_file=train_file.id,
                                  validation_file=test_file.id,
                                  hyperparameters={
                                              "n_epochs": 25, #10, 15
                                              "batch_size": 5,
                                              "learning_rate_multiplier": 1e-3
                                                  }
                                  )

# Monitor fine-tuning process
print(f"Fine-tuning job started: {fine_tune.id}")

import time
# Function to get fine-tune job status
def get_fine_tune_status(job_id):
    response = client.fine_tuning.jobs.retrieve(job_id)
    return response

# Monitor until the job is complete
job_id = fine_tune.id
status = client.fine_tuning.jobs.retrieve(job_id).status
if status not in ["succeeded", "failed"]:
    print(f"Job not in terminal status: {status}. Waiting.")
    while status not in ["succeeded", "failed"]:
        time.sleep(60)
        status = client.fine_tuning.jobs.retrieve(job_id).status
        print(f"Status: {status}")
else:
    print(f"Finetune job {job_id} finished with status: {status}")
print("Checking other finetune jobs in the subscription.")
result = client.fine_tuning.jobs.list()
print(f"Found {len(result.data)} finetune jobs.")

import signal
import datetime

def signal_handler(sig, frame):
    status = client.fine_tuning.jobs.retrieve(job_id).status
    print(f"Stream interrupted. Job is still {status}.")
    return

print(f"Streaming events for the fine-tuning job: {job_id}")

signal.signal(signal.SIGINT, signal_handler)

events = client.fine_tuning.jobs.list_events(fine_tuning_job_id=job_id)
try:
    for event in events:
        print(f'{datetime.datetime.fromtimestamp(event.created_at)} {event.message}')
except Exception:
    print("Stream interrupted (client disconnected).")

fine_tuned_model = result.data[0].fine_tuned_model
print(fine_tuned_model)

# Initialize the conversation history
conversation_history = [
    {"role": "system", "content": '''You are a friendly and accurate customer support assistant for Our company. Provide specific answers based on the user’s query while maintaining a conversational and engaging tone.
                                      Always ask for necessary details like product name, SKU, serial number, email, etc., if needed.
                                      If you are unsure about any information, ask for clarification or confirmation from the user rather than providing potentially inaccurate information.
                                      Your goal is to help the customer with the exact information they need while keeping the conversation flowing naturally.'''}
]
def detect_tone(text):
    from textblob import TextBlob as tb
    blob = tb(text)
    sentiment = blob.sentiment
    if sentiment.polarity > 0.1:
        return "positive"
    elif sentiment.polarity < -0.1:
        return "negative"
    else:
        return "neutral"

# Function to chat with the model using conversation history
def chat_with_model(user_input):
    # Append the user message to the conversation history
    tone = detect_tone(user_input)
    print('Tone:', tone)
    conversation_history.append({"role": "user", "content": f"{user_input}. The tone of this query is: {tone}"})

    # Get the model's response
    response = client.chat.completions.create(
        model=fine_tuned_model,
        messages=conversation_history
    )
    # Append the model's response to the conversation history
    conversation_history.append({"role": "assistant", "content": response.choices[0].message.content})

    return response.choices[0].message.content

# Continue the conversation
new_query = "I love this product!! Can i get a discount for a bulk order?"
response = chat_with_model(new_query)
print('User: ', new_query)
print('Bot: ', response)

"""##### Evaluating using Bert-Score for relevance, coherence and quality
- Used validation sample queries for the model response
- compared model responses with the existing bot response
"""

!pip install bert-score

from bert_score import score

# Reference responses and generated responses
references = [
  'We can help with that. Can you please provide your account email so we can guide you through updating your email preferences?',
 "Yes, you can use store credit for online purchases. Can you please provide the store credit number and the product name or SKU you're interested in?",
 "We'd be happy to help. Can you please provide the product name or SKU so we can provide you with the proper washing instructions?",
 'Certainly. Can you please provide the product name, SKU, or serial number, and a description of the part you need?',
 'We do offer free shipping on select orders. Can you please provide the product name or SKU and your shipping destination so we can check if your order qualifies?',
 "We'd be happy to assist you. Can you please provide the product name or SKU and a description of the customizations you'd like?",
 "We appreciate your feedback. Can you please provide a description of the issue you're experiencing and your email address so we can follow up with you?",
 "We'd be happy to provide information on our price adjustment policy. Can you please provide the product name or SKU so we can give you the most accurate information?",
 "We'd be happy to inform you of any upcoming sales or events. Can you please provide your email address so we can keep you updated?",
 "We'd be happy to help. Can you please provide your name, phone number, and the service you're interested in so we can schedule your appointment?",
 'Certainly. Can you please provide your order number or account email so we can locate your receipt and send you a copy?',
 "In some cases, we may accept competitor coupons. Can you please provide the competitor's coupon code and the product name or SKU you'd like to apply it to?",
 'Yes, we do have a recycling program. Can you please provide your email address so we can send you information on how to participate?',
 "We're sorry to hear that. Can you please provide the gift card number, if available, and your email address so we can assist you further?"
]

predictions = [
    'To help you update your email preferences, could you please specify if you are referring to email preferences for a specific product, service, or newsletter? This information will allow me to provide you with the most accurate instructions on how to change your email preferences.',
 'Absolutely! To assist you with using your store credit online, could you please provide the details of the store credit such as the store name, credit amount, and any unique code or number associated with it? This information will help me guide you on how to utilize your store credit for online purchases.',
 "I'd be happy to help with that! To provide you with the specific washing instructions, could you please share the name or description of the item you are inquiring about? This will allow me to give you accurate care instructions for that particular product.",
 'Of course! To assist you with getting a replacement part, could you please provide the product name, SKU, or serial number, and specify which part you need a replacement for? This information will help me guide you accurately.',
 'Yes, we do offer free shipping on select products and promotions. Could you please specify the product you are interested in or provide more details so I can confirm if free shipping is available for that item?',
 'Absolutely! We do offer custom orders for certain products. Could you please provide more details about the customization you are looking for or the specific product you are interested in customizing? This will help me assist you further with placing a custom order.',
 "I'm sorry to hear you're experiencing issues with our website. Could you please provide more details about the problem you are encountering, such as the specific page or feature that is not working correctly? This information will help me assist you in reporting the issue effectively.",
 'Our company typically offers price adjustments within a specific timeframe from the date of purchase. To provide you with accurate information, could you please specify the product you purchased and the date of your purchase? This will help me guide you on our policy regarding price adjustments.',
 'We often have sales and events throughout the year. To provide you with the most up-to-date information on upcoming sales or events, could you please let me know which product or category you are interested in or if there is a specific time frame you have in mind? This will help me give you more specific details.',
 "I'd be happy to help you schedule a consultation or appointment. Could you please provide more details about the type of consultation or appointment you are looking to schedule and for which product or service? This information will help me assist you in setting up the appointment efficiently.",
 'Certainly! To assist you in obtaining a copy of your receipt, could you please provide the order number, purchase date, and the email address associated with the order? This information will help me locate and provide you with a copy of your receipt.',
 "I appreciate your interest! At this time, we typically do not accept competitor's coupons. However, we do offer our own promotions and discounts. If you have any specific coupons or promotions you'd like to inquire about, feel free to share the details, and I can check if they are applicable at our store.",
 'Yes, we do have a recycling program for certain products. Could you please specify the type of product you are looking to recycle or provide more details so I can guide you on our recycling program and how to participate?',
 "I'm sorry to hear about your lost or stolen gift card. To assist you with reporting and potentially replacing the gift card, could you please provide the gift card number or any purchase details associated with the gift card? This information will help me guide you on the necessary steps to report and address the issue."
]

# Calculate BERTScore
P, R, F1 = score(predictions, references, lang="en", rescale_with_baseline=True)

# Print BERTScore results
print("Precision:", P.mean().item())
print("Recall:", R.mean().item())
print("F1 Score:", F1.mean().item())

"""- Precision: 0.5570733547210693
- Recall: 0.7520215511322021
- F1 Score: 0.6534156799316406
"""

