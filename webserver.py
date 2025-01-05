from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from urllib.parse import unquote, parse_qs

from sqlalchemy.exc import IntegrityError
from dotenv import load_dotenv 
from os import getenv
from model import async_main, Courses

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
from smtplib import SMTP
import re

@asynccontextmanager
async def lifespan(app: FastAPI):
    await async_main()
    print("Open")
    yield
    print("Close")

app = FastAPI(lifespan = lifespan)


@app.get("/")
async def Hello():
    return "It`s a get request"

@app.post("/")
async def receive_data(request: Request):
    try:
        body = await request.body() # Чтение данных из тела запроса
        data = re.sub(r'[{"}]', "", unquote(body.decode()).replace(",", "&").replace(":","=")) # Декодируем байты в строку
        parsed_data = parse_qs(data)
        for key, value in parsed_data.items():
            parsed_data[key] = value[0]
    except Exception as e:
        print(f"\n{e}\n")

    try:
        links = await Courses.Create_User(parsed_data["Email"], parsed_data["Phone"], parsed_data["products"])
        await SendMail(parsed_data["Email"], links, parsed_data["Name"], parsed_data["products"])
        return JSONResponse(status_code = 200, content = {"message": "Data received"})
    except IntegrityError:
        links = await Courses.Update_User(parsed_data["Email"], parsed_data["Phone"], parsed_data["products"])
        await SendMail(parsed_data["Email"], links, parsed_data["Name"], parsed_data["products"])
        return JSONResponse(status_code = 200, content = {"message": "Data received"})
    except Exception as e:
        print(f"\nОтправка email\n{e}\n")
        return JSONResponse(status_code = 500, content = {"message": "Data not received"})
        
    

async def SendMail(recipient_email: str, link: str, name: str, course: str):
    try:
        load_dotenv()
        smtp_server = smtplib.SMTP("smtp.gmail.com", 587)
        smtp_server.starttls()
        smtp_server.login(getenv("ELOGIN"), getenv("EPASSWORD"))
        c = re.sub(r'[1234567890.=]', '', course.replace('[', '').replace(']', ''))
        link_list = link.split(" | ")

        msg = MIMEMultipart()
        msg["From"] = getenv("ELOGIN")
        msg["To"] = recipient_email
        msg["Subject"] = f"Приветствуем на курсе «Пилочный для тебя», {c} от Александры Воропаевой✨"

        if (getenv("2COURSE_NAME") in course) or (getenv("3COURSE_NAME") in course) or (getenv("UPDATE_NAME") in course):
            mes = f"{name} \nВидеоуроки: {link_list[0]} \nЧат обратной связи: {link_list[1]}"
            
        else:
            mes = f"{name} \nСсылка: {link}"
        
        text = mes
        msg.attach(MIMEText(text, "plain"))

    except Exception as e:
        print(e)

    finally:
        smtp_server.sendmail(getenv("ELOGIN"), recipient_email, msg.as_string())
        smtp_server.quit()