FROM public.ecr.aws/lambda/python:3.9
COPY --from=openjdk:11 /usr/local/openjdk-11 /usr/local/openjdk-11
ENV JAVA_HOME /usr/local/openjdk-11
ENV PATH $PATH:$JAVA_HOME/bin
RUN java --version
RUN python --version
COPY * ./
RUN pip install -r requirements.txt
CMD ["app.lambda_handler"]