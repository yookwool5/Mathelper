import streamlit as st
from PIL import Image
from openai import OpenAI
import requests
import json
import base64
import io

st.title('MATHELPER')
st.write('This is a math problem helper based on ChatGPT API (By Gyurim Hwang)')

with st.sidebar:
    openai_api_key = st.text_input(label = "OPENAI API KEY", placeholder = "Enter Your ChatGPT API key", value='', type = 'password')
    st.markdown("---")
    mathpix_app_key = st.text_input(label = "MATHPIX API KEY", placeholder = "Enter Your Mathpix API key", value='', type = 'password')
    mathpix_app_id = st.text_input(label = "MATHPIX API ID", placeholder = "Enter Your Mathpix API key", value='', type = 'password')
    st.markdown("---")
    openai_model = st.radio(label = "GPT Model", options = ["gpt-4", "gpt-3.5-turbo"])
    st.markdown("---")
    st.button(label = "초기화")

headers = {
        'app_id': mathpix_app_id,
        'app_key': mathpix_app_key,
        'Content-Type': 'application/json'
}
MATHPIX_API_URL = "https://api.mathpix.com/v3/text"

def image_to_mathpix(image):
    # 이미지를 base64로 인코딩
    buffered = io.BytesIO()
    image.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode()

    # Mathpix API로 요청 보내기
    data = {
        'src': f'data:image/png;base64,{img_str}',
        'formats': ['text', 'latex'],  # 'formats'에 텍스트와 LaTeX을 포함
    }
    
    response = requests.post(MATHPIX_API_URL, headers=headers, json=data)
    return response.json()


client = OpenAI(api_key=openai_api_key)
level_message = {
    "Weak" : "You should let me know the essential mathematical concept or keyword for this problem. And give some brief explanation about them. You shouldn't give the answer or direct hint" ,
    "Medium" : "You are an study assistant that gives hints without providing answer" ,
    "Strong" : "You are a tutor for this math problem. Give full hint for this problem, just avoiding giving direct answer"
}

def gpt_hinter(problem, hint_level):
    prompt = f"정답을 제시하지 않고, 다음 수학 문제에 대한 힌트를 줘: {problem}"
    response = client.chat.completions.create(
        model=openai_model,
        messages=[{"role":"user", "content":problem},
                 {"role":"system", "content":level_message[hint_level]}]
    )
    return response


uploaded_file = st.file_uploader("Upload your problem image", type=["png", "jpg", "jpeg"])

hint_level = st.radio(label = "Hint Level", options = ["Weak", "Medium", "Strong"])

if uploaded_file is not None:
    # 업로드한 이미지를 열고 화면에 표시
    image = Image.open(uploaded_file)
    st.image(image, caption="Uploaded Image", use_column_width=True)
    
    if st.button("Get A Hint !"):
        result = image_to_mathpix(image)
        # ChatGPT API로 질문 보내기
        print(result)
        response = gpt_hinter(result['text'], hint_level)
        
        # ChatGPT의 응답 표시
        answer = response.choices[0].message.content
        st.write("Try This Way !")
        st.write(answer)

