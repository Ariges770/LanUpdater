# Dockerfile

FROM python:3.9-slim

# Create user
RUN groupadd --gid 1000 user \
    && useradd --uid 1000 --gid 1000 --create-home --shell /bin/bash user \
    && chown -R "1000:1000" /home/user

# Move script inside container
RUN mkdir -p /home/user/scripts

ADD main/lan_ip_logger.py /home/user/scripts

# Update ownership and permissions
RUN chown -R 1000:1000 /home/user/scripts \
    && chmod -R 755 /home/user/scripts

USER user

# COPY lan_ip_logger.py /app

RUN pip install --upgrade pip && pip install python-dotenv requests

WORKDIR /home/user/scripts

CMD ["python", "lan_ip_logger.py"]
