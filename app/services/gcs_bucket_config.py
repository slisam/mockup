import yaml
import os

BUCKET_NAME = os.environ["BUCKET"]
ALL_JOBS_ROOT_PATH = os.environ["ALL_JOBS_ROOT_PATH"]
MAIN_JOB_ROOT_PATH = (ALL_JOBS_ROOT_PATH+"/transformation-{transformation_id}")
MAIN_JOB_RATE_CARD_PATH = MAIN_JOB_ROOT_PATH + "/rate-card"
MAIN_JOB_SOP_PATH = MAIN_JOB_ROOT_PATH + "/sop"
RATE_CARD_PATH = MAIN_JOB_RATE_CARD_PATH + "/rate_card.xlsx" #xlsx
SOP_PATH = MAIN_JOB_SOP_PATH + "/sop.docx" #docx
APPROVER_COMMENT_PATH = MAIN_JOB_ROOT_PATH + "/approver-comment/approver_comment.json" #TransformationInput


MAIN_JOB_STATUS_PATH = MAIN_JOB_ROOT_PATH + "/status"
SUB_JOB_PATH = (MAIN_JOB_ROOT_PATH + "/job-{job_name}")
SUB_JOB_OUTPUT_PATH = SUB_JOB_PATH + "/output"
SUB_JOB_OUTPUT_AUTOMATED_PATH = SUB_JOB_OUTPUT_PATH + "/automated/output.json"
SUB_JOB_OUTPUT_MODIFIED_PATH = SUB_JOB_OUTPUT_PATH + "/modified/output.json"
JOBS_CONFIG_PATH = os.path.join(os.path.dirname(__file__), "jobs.yml")


# SOP_PARSED_PATH = SUB_JOB_OUTPUT_PATH + "/sop_parsed.json"
# RC_PARSED_CONCATENATED_PATH = SUB_JOB_OUTPUT_PATH + "/rc_parsed_concatenated.txt"
# RC_PARSED_BY_SHEET_PATH = SUB_JOB_OUTPUT_PATH + "/rc_parsed_by_sheets.json"
# RC_PARSED_DOCLING_PATH = SUB_JOB_OUTPUT_PATH + "/rc_parsed_docling.json"

def get_jobs_config() -> dict[int, str]:    

    # Load YAML file
    with open(JOBS_CONFIG_PATH, 'r') as file:
        jobs_config = yaml.safe_load(file)
    
    # get the list of the jobs
    jobs_config_list = jobs_config['jobs']

    # transform the list into a dict
    jobs_config_dict = {job["id"] : job["name"] for job in jobs_config_list}

    return jobs_config_dict


def get_sub_job_name_from_id(id : int) -> str:
    jobs_config_dict = get_jobs_config()
    return jobs_config_dict[id]