from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import time
from django.shortcuts import render
from django.http import JsonResponse
import speech_recognition as sr
from django.utils.html import escape
import google.generativeai as genai
from googletrans import Translator, LANGUAGES
from langdetect import detect




genai.configure(api_key='AIzaSyCo870-t1sjOB4bASzJ4A0rYe0Wjil3SgA')
translator = Translator()
generation_config = {
  "temperature": 1,
  "top_p": 0.95,
  "top_k": 64,
  "max_output_tokens": 8192,
  "response_mime_type": "text/plain",
}
safety_settings = [
  {
    "category": "HARM_CATEGORY_HARASSMENT",
    "threshold": "BLOCK_MEDIUM_AND_ABOVE",
  },
  {
    "category": "HARM_CATEGORY_HATE_SPEECH",
    "threshold": "BLOCK_MEDIUM_AND_ABOVE",
  },
  {
    "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
    "threshold": "BLOCK_MEDIUM_AND_ABOVE",
  },
  {
    "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
    "threshold": "BLOCK_MEDIUM_AND_ABOVE",
  },
]

model = genai.GenerativeModel(
  model_name="gemini-1.5-flash",
  safety_settings=safety_settings,
  generation_config=generation_config,
)

model2=genai.GenerativeModel(
  model_name="gemini-pro-vision")

chat_session = model.start_chat(
  history=[
  ]
)

@csrf_exempt
def fetch_language(request):
  if request.method == 'POST':
    data = json.loads(request.body)
    selected_language = data.get('language','english')
    request.session['selected_language'] = selected_language
    print(selected_language)
    # Process the selected language here (optional)
    return JsonResponse({'status': 'success'})
  else:
    return JsonResponse({'status': 'error'})

# In other parts of your application:
# Use the selected_language for processing, displaying content, etc.

def home(request):
    return render(request, 'home.html')

import re
from mistletoe import markdown

def convert_to_html(text):
    # Replace markdown headings with HTML headings
    text = re.sub(r'##\s(.*?)\n\n', r'<h2>\1</h2>', text)

    # Replace bold text markdown with HTML strong tags
    text = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', text)

    # Replace asterisk bullet points with HTML ul and li tags
    text = re.sub(r'\*\s(.*?)\n', r'<li>\1</li>', text)
    text = re.sub(r'<li>(.*?)</li>', r'<ul>\1</ul>', text)

    # Replace line breaks with HTML paragraph tags
    text = '<p>' + re.sub(r'\n{2,}', r'</p><p>', text) + '</p>'

    return text

@csrf_exempt
def send_message(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        print(data)
        message = data.get('message', '')
        selected_language = request.session.get('selected_language','English')

        
        print(selected_language)
  
        
        languages = {
            'Hindi': 'hi',
            'English': 'en',
            'Tamil': 'ta',
            'Telugu': 'te',
            'Marathi': 'mr',
            'Bengali': 'bn',
            'Gujarati': 'gu',
            'Malayalam': 'ml',
            'Kannada': 'kn',
            'Urdu': 'ur',
            'Spanish': 'es',
            'French': 'fr',
            'German': 'de'
        }

        language_code = languages.get(selected_language, 'en')
        
        
        if language_code != 'en':
            translated_message = translator.translate(message, src=language_code, dest='en').text
        else:
            translated_message = message
        
        response = chat_session.send_message(translated_message)
        
        

        # Extract the generated text from the API response
        response_text = response.text
        
        print(response_text)
        translated_summary = translator.translate(response.text, src='en', dest=language_code).text  
        print("T   ",translated_summary)    
        
        html_text=convert_to_html(translated_summary)  
        print(html_text)

        # mark_text=markdown(response_text)
        
        
        return JsonResponse({'response': html_text,'lang':selected_language})

import PIL.Image
from PIL import Image


@csrf_exempt  # This decorator allows the view to accept POST requests without CSRF token
def upload_image(request):

    if request.method == 'POST':
        # Get the uploaded image from the request
        uploaded_image = request.FILES.get('image')
        description = request.POST.get('description', '')
        selected_language = request.session.get('selected_language','english')
        
        

        if uploaded_image:
            # Process the image and description (replace this with your actual processing logic)
            # For example, you can analyze the image and generate a response based on its content
            # You can use machine learning models, image processing libraries, or any other method
            
            languages = {
                    'Hindi': 'hi',
                    'English': 'en',
                    'Tamil': 'ta',
                    'Telugu': 'te',
                    'Marathi': 'mr',
                    'Bengali': 'bn',
                    'Gujarati': 'gu',
                    'Malayalam': 'ml',
                    'Kannada': 'kn',
                    'Urdu': 'ur',
                    'Spanish': 'es',
                    'French': 'fr',
                    'German': 'de'
                }

            language_code = languages.get(selected_language, 'en')
            if description:
                
                

        
                print(selected_language)
          
                
                
                
                
                if language_code != 'en':
                    dec_message = translator.translate(description, src=language_code, dest='en').text
                else:
                    dec_message = description
            else:
                dec_message = "write a note about describing the image indetail"
            image = Image.open(uploaded_image)
            response=model2.generate_content([dec_message,image],)
            response.resolve()
            
            
            translated_summary = translator.translate(response.text, src='en', dest=language_code).text  
            print("T   ",translated_summary)    
                
            html_text=convert_to_html(translated_summary)  
            print(html_text)
            
            answer=markdown(response.text)
            print(markdown(response.text))
            
            # Return the response
            return JsonResponse({'response': html_text,'lang':selected_language})
        else:
            # Return an error response if no image is uploaded
            return JsonResponse({'error': 'No image uploaded'}, status=400)
    else:
        # Return an error response if the request method is not POST
        return JsonResponse({'error': 'Invalid request method'}, status=405)

@csrf_exempt
def send_audio(request):
    if request.method == 'POST' and request.FILES.get('audio'):
        audio_file = request.FILES['audio']
        recognizer = sr.Recognizer()
        
        print(" df ")
        possible_languages = []
        languages = {
            'Hindi': 'hi',
            'English': 'en',
            'Tamil': 'ta',
            'Telugu': 'te',
            'Marathi': 'mr',
            'Bengali': 'bn',
            'Gujarati': 'gu',
            'Malayalam': 'ml',
            'Kannada': 'kn',
            'Urdu': 'ur',
            'Spanish': 'es',
            'French': 'fr',
            'German': 'de'
        }
        
        with sr.AudioFile(audio_file) as source:
            audio_data = recognizer.record(source)
            try:
                for language_code in languages.values():
                    try:
                        text = recognizer.recognize_google(audio_data, language=language_code)
                        possible_languages.append((language_code, text))  # Store recognized text for each language
                    except sr.UnknownValueError:
                        pass
                print("list ===   ",possible_languages)
                text = recognizer.recognize_google(audio_data)
                response_text = generate_response(text)  # This should be your function to generate AI responses based on text input
                
                
                selected_language = request.session.get('selected_language','english') 
                # response = chat_session.send_message(message)
        # Extract the generated text from the API response
                response_text = response.text
                languages = {
            'Hindi': 'hi',
            'English': 'en',
            'Tamil': 'ta',
            'Telugu': 'te',
            'Marathi': 'mr',
            'Bengali': 'bn',
            'Gujarati': 'gu',
            'Malayalam': 'ml',
            'Kannada': 'kn',
            'Urdu': 'ur',
            'Spanish': 'es',
            'French': 'fr',
            'German': 'de'
        }

                language_code = languages.get(selected_language, 'en')
        
                print(response_text)
                translated_summary = translator.translate(response.text, src='en', dest=language_code).text  
                print("T   ",translated_summary)    
        
                html_text=convert_to_html(translated_summary)  
                print(html_text)

                mark_text=markdown(response_text)
        
        
                return JsonResponse({'response': html_text})
            except sr.UnknownValueError:
                return JsonResponse({'response': "Sorry, I could not understand the audio."})
            except sr.RequestError:
                return JsonResponse({'response': "Sorry, there was an error processing the audio."})

    return JsonResponse({'response': "Invalid request."})




# @csrf_exempt
# def fetch_language(request):
#   if request.method == 'POST':
#     data = json.loads(request.body)
#     print(data)
      
#     selected_language = data.get('language')
#     print(selected_language)
#     # Process the selected language here (optional)
#     return JsonResponse({'status': 'success'})  # Or your desired response
#   else:
#     return JsonResponse({'status': 'error'})