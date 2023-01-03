from django.apps import AppConfig
##################################################
## Uncomment if you want to apply the AI model ###
##################################################
# from .ai_model.model import Agent
# import torch


class FinalystAppConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "finalyst_app"
    ##################################################
    ## Uncomment if you want to apply the AI model ###
    ##################################################
    # generator = Agent('C:/Users/s_mmin/Desktop/Finalyst/FinBERT_Korean_Corporate_Financial_Issue_Resolution_Model/finalyst/finalyst_app/ai_model/data/comment_2022_Q1_naver.csv', 'C:/Users/s_mmin/Desktop/Finalyst/FinBERT_Korean_Corporate_Financial_Issue_Resolution_Model/finalyst/finalyst_app/ai_model/best_model', device=torch.device('cpu'))

