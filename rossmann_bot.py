import pandas as pd
import json
import requests
from flask import Flask, request, Response
import os
from rossmann_bot import rossmann_bot

#constants
TOKEN='6529866802:AAGBVGIncX84MehWXfD-so8Pkds3A94Unn8'

# How get telegram API`s info
# # Bot info
# https://api.telegram.org/bot6529866802:AAGBVGIncX84MehWXfD-so8Pkds3A94Unn8/getMe

# # Get updates
# https://api.telegram.org/bot6529866802:AAGBVGIncX84MehWXfD-so8Pkds3A94Unn8/getUpdates

# # Send message
# https://api.telegram.org/bot6529866802:AAGBVGIncX84MehWXfD-so8Pkds3A94Unn8/sendMessage?chat_id=1218019388&text=hello TCS


def send_message(chat_id, text):
    url= 'https://api.telegram.org/bot{}/'.format(TOKEN)
    url= url + 'sendMessage?chat_id={}'.format(chat_id)
    request.post(url, json={'text': text})
    print('Status Code {}'.format(r.status_code))

    return None

def load_dataset(store_id):
        """
    Loads a dataset for a given store ID.
    Parameters:
        store_id (int): The ID of the store for which to load the dataset.
    Returns:
        str: A JSON string representing the loaded dataset.
    """
    # loading test dataset
    df10 = pd.read_csv("test.csv")
    df_store_raw = pd.read_csv("store.csv")

    # merge test dataset + store
    df_test = pd.merge(df10, df_store_raw, how="left", on="Store")

    # choose store for prediction
    df_test = df_test[df_test["Store"] == 22]

    if not df_test.empty:
        # remove closed days
        df_test = df_test[df_test["Open"] != 0]
        df_test = df_test[~df_test["Open"].isnull()]
        df_test = df_test.drop("Id", axis=1)
        # df_test.head()

        # convert Dataframe to json
        data = json.dumps(df_test.to_dict(orient="records"))

    else:
        data = 'error'
        
    return data

def predict(data):
    """
    Makes a POST request to the Rossmann API to retrieve a prediction based on the provided data.
    Parameters:
        data (str): A JSON string representing the data to be sent in the POST request.
    Returns:
        pd.DataFrame: A pandas DataFrame containing the prediction result.
    """
    # API Call
    url = "https://rossman-case.onrender.com/rossmann/predict"
    header = {"Content-type": "application/json"}
    data = data


    r = requests.post(url, data=data, headers=header)
    print("Status Code {}".format(r.status_code))

    d1 = pd.DataFrame(r.json(), columns=r.json()[0].keys())

    return d1


def parse_message(message):
    chat_id = message['message']['chat']['id']
    store_id = message['message']['text']
    
    store_id = store_id.replace('/', '')
    
    try:
        store_id = int(store_id)
        
    except ValueError:
        store_id = 'error'
        return
    
    return chat_id, store_id


# API initiallization
app = Flask(__name__)

@app.route('/', methods=['POST', 'GET'])
def index():
    if request.method = 'POST':
        message=requests.get_json()
        chat id, store_id= parse_message(message)
        
        if store_id != 'error':
            # loading data
            data = load_dataset(store_id)
            
            if data != 'error':
            # prediction
            d1 = predict(data)
            
            # calculation
            d2 = d1[['store', 'prediction']].groupby("store").sum().reset_index()

            msg = 'Store Number {} will sell US${:,.2f} in the next 6 weeks'.format(
            d2['store'].values[0]
            d2['prediction'].values[0]
            )
            send_message(chat_id, 'Store ID is wrong')
            return Response('ok', status=200)            
            
            else:
                send_message(chat_id, 'Store ID is wrong')
                return Response('ok', status=200)
            
        else:
            send_message(chat_id, 'Store ID is wrong')
            return Response('ok', status=200)
            
    else:
            return '<h1> Rossmann Telegram Bot </h1>'
        
if __name__ == '__main__':
    port = os.environ.get('PORT', 5000)
    app.run(host='0.0.0.0', port=5000)
