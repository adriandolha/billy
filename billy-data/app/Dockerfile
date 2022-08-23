FROM public.ecr.aws/lambda/python:3.9
COPY --from=public.ecr.aws/ews-network/amazoncorretto:17 /usr/lib/jvm/java-17-amazon-corretto /usr/lib/jvm/java-17-amazon-corretto
ENV JAVA_HOME /usr/lib/jvm/java-17-amazon-corretto
ENV PATH $PATH:$JAVA_HOME/bin
RUN java --version
RUN python --version
COPY requirements.txt ${LAMBDA_TASK_ROOT}/
RUN pip install -r requirements.txt
RUN echo ${LAMBDA_TASK_ROOT}
COPY . ${LAMBDA_TASK_ROOT}/
CMD ["app.lambda_handler"]