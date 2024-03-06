import streamlit as st
import easyocr
import pymysql
import cv2
import numpy as np 
import pandas as pd
from PIL import Image

#----------------------------------------------------Creating connection with mysql workbench--------------------------------------------------------#

my_db = pymysql.connect(
    host="localhost",
    user="root",
    password="Ramkumar$7",
    database="card")

cursor = my_db.cursor()

#----------------------------------------------------Create a table and store the info in it--------------------------------------------------------#

cursor.execute("CREATE TABLE IF NOT EXISTS card_data (id INT AUTO_INCREMENT PRIMARY KEY, name VARCHAR(255), job_title VARCHAR(255), address VARCHAR(255), postcode VARCHAR(255), phone VARCHAR(255), email VARCHAR(255), website VARCHAR(255), company_name VARCHAR(225))")

#----------------------------------------------------Create a EASYOCR Environment-------------------------------------------------------------------#
ocr_reader = easyocr.Reader(['en'])

#----------------------------------------------------Set page configurations------------------------------------------------------------------------#

icon = Image.open("/Users/Ram kumar/Downloads/business-card-data-extraction.jpg")

st.set_page_config(page_title= "BizCardX: Extracting Business Card Data with OCR ",
                   page_icon= icon,
                   layout= "wide",
                   initial_sidebar_state= "expanded",
                   menu_items={'About': """# This OCR app is created by Arockia Joe Snow A"""})
st.markdown("<h1 style='text-align: center; color: green;'>BizCardX: Extracting Business Card Data with OCR ❖</h1>", unsafe_allow_html=True)

st.markdown(
         f"""
         <style>
         .stApp {{
             background-image: url("https://edge.mwallpapers.com/photos/celebrities/colors/md/plain-white-wallpaper-android-iphone-hd-wallpaper-background-downloadhd-wallpapers-desktop-background-android-iphone-1080p-4k-svkr8.jpg");
             background-attachment: fixed;
             background-size: cover
         }}
         </style>
         """,
         unsafe_allow_html=True
         
        )
#display 
st.title(":blue[Extracting Business Card Data with OCR]")

#--------------------------------------------------Create a file uploader widget-------------------------------------------------------------------#

uploaded_file = st.file_uploader("Upload a business card image", type=["jpg", "jpeg", "png"])

#--------------------------------------------------Create a selectbox tool-------------------------------------------------------------------------#

choice = ['Home','Add', 'View', 'Update', 'Delete']
selected = st.sidebar.selectbox("Select an option", choice)

if selected == "Home":
    st.markdown("## :red[**Technologies Used :**]")
    st.write("## :black[Python,easy OCR, Streamlit, SQL, Pandas]")
    st.markdown("## :red[**Overview :**]")
    st.write("## :black[In this streamlit web app you can upload an image of a business card and extract relevant information from it using easyOCR. You can view, modify or delete the extracted data in this app. This app would also allow users to save the extracted information into a database along with the uploaded business card image. The database would be able to store multiple entries, each with its own business card image and extracted information]")
elif selected == 'Add':
    if uploaded_file is not None:
        #------------------------------------------Read the image using OpenCV--------------------------------------------------------------------#
        
        image = cv2.imdecode(np.fromstring(uploaded_file.read(), np.uint8), 1)
        st.image(image, caption='Uploaded business card image', use_column_width=True)
        
        #------------------------------------------Create a button to extract---------------------------------------------------------------------#
        
        if st.button('Extract'):
           
            #--------------------------------------Call the function to extract the information and convert into string---------------------------#
            
            bounds = ocr_reader.readtext(image, detail=0)
            text = "\n".join(bounds)
            
            #--------------------------------------Upload information and image into the database-------------------------------------------------#
            
            mysql_info = "INSERT INTO card_data(name, job_title, address, postcode, phone, email, website, company_name) VALUES ( %s, %s, %s, %s, %s, %s, %s, %s)"
            values = (bounds[0], bounds[1], bounds[2], bounds[3], bounds[4], bounds[5], bounds[6], bounds[7])
            cursor.execute(mysql_info, values)
            my_db.commit()
            
            #--------------------------------------Data successfully added into Database----------------------------------------------------------#
            
            st.success("Business card information added to database.")
elif selected == 'View':
    
    #----------------------------------------------Display the informations as a Dataframe--------------------------------------------------------#
    cursor.execute("SELECT * FROM card_data")
    result = cursor.fetchall()
    df = pd.DataFrame(result, columns=['id','name', 'job_title', 'address', 'postcode', 'phone', 'email', 'website', 'company_name'])
    st.write(df)

elif selected == 'Update':
    
    #----------------------------------------------Select a Business card to update---------------------------------------------------------------#
    
    cursor.execute("SELECT id, name FROM card_data")
    result = cursor.fetchall()
    business_cards = {}
    for row in result:
        business_cards[row[1]] = row[0]
    selected_card_name = st.selectbox("Select a business card to update", list(business_cards.keys()))
    
    #----------------------------------------------Get the  information for the selected card-----------------------------------------------------#
    
    cursor.execute("SELECT * FROM card_data WHERE name=%s", (selected_card_name,))
    result = cursor.fetchone()

    #----------------------------------------------Display the current information----------------------------------------------------------------#
    
    st.write("Name:", result[1])
    st.write("Job Title:", result[2])
    st.write("Address:", result[3])
    st.write("Postcode:", result[4])
    st.write("Phone:", result[5])
    st.write("Email:", result[6])
    st.write("Website:", result[7])
    st.write("company_name:", result[8])

    #----------------------------------------------Add new information----------------------------------------------------------------------------#
   
    name = st.text_input("Name", result[1])
    job_title = st.text_input("Job Title", result[2])
    address = st.text_input("Address", result[3])
    postcode = st.text_input("Postcode", result[4])
    phone = st.text_input("Phone", result[5])
    email = st.text_input("Email", result[6])
    website = st.text_input("Website", result[7])
    company_name = st.text_input("Company Name", result[8])

    #----------------------------------------------Create a button to update the card-------------------------------------------------------------#
    
    if st.button("Update Business Card"):
        
        #------------------------------------------Update the information for the selected card in the database-----------------------------------#
        
        cursor.execute("UPDATE card_data SET name=%s, job_title=%s, address=%s, postcode=%s, phone=%s, email=%s, website=%s, company_name=%s WHERE name=%s", 
                             (name, job_title, address, postcode, phone, email, website, company_name, selected_card_name))
        my_db.commit()
        st.success("Business card information updated in database.")
elif selected == 'Delete':
   
    #----------------------------------------------Select a business card to delete---------------------------------------------------------------#
    
    cursor.execute("SELECT id, name FROM card_data")
    result = cursor.fetchall()
    business_cards = {}
    for row in result:
        business_cards[row[0]] = row[1]
    selected_card_id = st.selectbox("Choose a card to delete", list(business_cards.keys()), format_func=lambda x: business_cards[x])

    #----------------------------------------------Get the name of the selected card--------------------------------------------------------------#
   
    cursor.execute("SELECT name FROM card_data WHERE id=%s", (selected_card_id,))
    result = cursor.fetchone()
    selected_card_name = result[0]

    #----------------------------------------------Display the current information for the selected card------------------------------------------#
    
    st.write("Name:", selected_card_name)
    
    #----------------------------------------------Insert a button to delete the selected card----------------------------------------------------#
    
    if st.button("Delete Business Card"):
        cursor.execute("DELETE FROM card_data WHERE name=%s", (selected_card_name,))
        my_db.commit()
        st.success("Card information deleted from MYSQL.")