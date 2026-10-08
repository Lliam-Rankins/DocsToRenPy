FROM python
RUN pip install pytest
ENV TEST="false"

# Set work dir and copy the repo from the runner
WORKDIR /opt/app
COPY . .

# If TESTing then run pytest
CMD if [ "$TEST" = "true" ]; then python -m pytest; fi