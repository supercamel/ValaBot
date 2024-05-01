import openai
import time

# set the openai host and port
openai.api_base = "http://127.0.0.1:5001/v1"

def tryMessages(messages, model="gpt-4-0314"):
    while True:
        try:
            response = openai.ChatCompletion.create(
                model=model,
                messages=messages
            )
            return response["choices"][0]["message"]["content"].strip()
        except Exception as e:
            # if it's an openai.error.RateLimitError, wait 10 seconds and try again
            if type(e) == openai.error.RateLimitError:
                print("rate limit error, waiting 10 seconds and trying again")
                time.sleep(10)
            elif type(e) == openai.error.ServiceUnavailableError:
                print("service unavailable error, waiting 10 seconds and trying again")
                time.sleep(20)
            elif type(e) == openai.error.APIError:
                print("api error, waiting 10 seconds and trying again")
                print(e)
                time.sleep(10)
            else:
                raise e