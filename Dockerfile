FROM python
EXPOSE 5000
COPY requirements.txt /requirements.txt
RUN sed -Ei 's/==/>=/' /requirements.txt 
RUN pip install -r /requirements.txt 
RUN rm /requirements.txt