echo '>>> Create virtual environment >>>'
virtualenv lambda_venv
echo '\n>>> Activate virtual environment >>>'
source lambda_venv/bin/activate
echo '\n>>> Install python dependencies >>>'
pip install -r requirements.txt
cd lambda_venv/lib/python3.9/site-packages
echo '\n>>> Make a zip of python dependencies >>>'
zip -r9 ${OLDPWD}/python-discord-bot.zip .
cd $OLDPWD
echo '\n>>> Add constants.py into the zip >>>'
zip -g python-discord-bot.zip constants.py
echo '\n>>> Add lambda_function.py into the zip >>>'
zip -g python-discord-bot.zip lambda_function.py
echo '\n>>> Upload the zip into the S3 bucket >>>'
aws s3 cp --profile discord_bot python-discord-bot.zip s3://7span-discord-bot-lambda-code/
echo '\n>>> Update Lambda funtion with the latest S3 zip >>>'
aws lambda --profile discord_bot update-function-code --function-name python-discord-bot --s3-bucket 7span-discord-bot-lambda-code --s3-key python-discord-bot.zip