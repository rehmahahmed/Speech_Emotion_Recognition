# Speech_Emotion_Recognition
A project integrating responsive and functional virtual assistant capabilities with Emotion recognition via speech.

Speech Emotion Recognition Software (SERS) is a smart AI tool that can converse via speech or text, respond well to any prompts and questions, perceive voice features and evaluate emotion behind one’s voice.

The project is purely python coded. The emotion detection system is based on the ML model available on the repository. The model is trained on Ryerson Audio-Visual Database of Emotional Speech and Song (RAVDESS). The dataset consists of 24 actors(12 Male, 12 Female) recordings of 8 emotions. 

The model uses preprocessed dataset that is trained on 4 emotions that are Happy, Neutral, Sad and Angry. The model checks for features such as Chroma, Mel, MFCC (Mel-frequency cepstral coefficients) to train with the help of MLPClassifier (Multi-layer Perceptron classifier) which is a model that relies on an underlying Neural Network to perform the task of classification.

Prediction features are extracted with the help of python’s Librosa library. Librosa is valuable Python music and sound investigation library that helps programming designers to fabricate applications for working with sound and music.

For Chatbot and NLP, the project uses Openai’s API. The user prompts are sent to Openai servers and a fitting response is sent back to the software with the help of API key.

For profiles, login data and emotion history the software uses SQL database. The database stores usernames, passwords, profile-picture and recent history of emotions.


![Rehmah Black Book_page-0037](https://github.com/rehmahahmed/Speech_Emotion_Recognition/assets/95929046/883f6ff1-fb3e-4a32-ba82-791fb3fe8ad5)
![Rehmah Black Book_page-0038](https://github.com/rehmahahmed/Speech_Emotion_Recognition/assets/95929046/ee30df93-7b1e-4f67-9888-cd16165b839c)
![Rehmah Black Book_page-0039](https://github.com/rehmahahmed/Speech_Emotion_Recognition/assets/95929046/407d7bcb-2126-4a48-a701-9ed8674cc894)
![Rehmah Black Book_page-0040](https://github.com/rehmahahmed/Speech_Emotion_Recognition/assets/95929046/527ea198-96da-474e-baf4-d3d86fce4094)
![Rehmah Black Book_page-0041](https://github.com/rehmahahmed/Speech_Emotion_Recognition/assets/95929046/69194f25-28ad-412f-9818-b87bfbfdd068)
![Rehmah Black Book_page-0036](https://github.com/rehmahahmed/Speech_Emotion_Recognition/assets/95929046/4f94d2f2-0569-4b1b-bea2-89b20f4ce23d)

