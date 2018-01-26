FROM python:3.6

WORKDIR /usr/src/cryptoverse

COPY . .
#RUN python setup.py test
#RUN python setup.py install
#RUN pip install --no-cache-dir -r requirements.txt

CMD ["bash"]
