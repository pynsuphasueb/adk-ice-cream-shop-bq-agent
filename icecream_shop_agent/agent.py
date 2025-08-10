import google.auth
from dotenv import load_dotenv
from google.adk.agents import Agent
from google.adk.tools.bigquery import BigQueryCredentialsConfig, BigQueryToolset
from google.adk.tools.bigquery.config import BigQueryToolConfig, WriteMode

GEMINI_MODEL = "gemini-2.5-flash"

load_dotenv()

adc, _ = google.auth.default()
bq_toolset = BigQueryToolset(
    credentials_config=BigQueryCredentialsConfig(credentials=adc),
    bigquery_tool_config=BigQueryToolConfig(write_mode=WriteMode.BLOCKED),
)

root_agent = Agent(
    model=GEMINI_MODEL,
    name="icecream_shop_agent",
    description="Answer questions and run read-only BigQuery queries.",
    instruction="""
    คุณเป็น Data Agent ที่ตอบคำถามด้วย BigQuery tools เท่านั้น
    กฎสำคัญ (ต้องทำตามเคร่งครัด):
    1) อนุญาตให้คิวรีเฉพาะ Dataset: `project_name.dataset_name.icecream_shop`
    2) เวลาเขียน SQL ต้องใส่ตารางแบบ fully-qualified เสมอ เช่น
    `SELECT ... FROM `project_name.dataset_name.icecream_shop`
    3) ห้ามอ้างอิง dataset/project อื่น, ห้าม `INFORMATION_SCHEMA` นอก dataset นี้
    4) ถ้าผู้ใช้ขอข้อมูลนอกขอบเขต ให้ปฏิเสธอย่างสุภาพและแนะนำให้ย้ายข้อมูลมาที่ dataset นี้ก่อน

    ตัวอย่างที่ถูก:
    - FROM `project_name.dataset_name.icecream_shop`
    ตัวอย่างที่ผิด:
    - FROM `project_name.other_ds.some_table`
    - FROM `public-project.*.*`
    
    Formatting guidelines:
    - Use plain text for lists and rankings, starting each item with '- '.
    - For example:
      ยอดขายรวม 5 อันดับแรกตามสาขา:
      - สาขา A: 123 บาท
      - สาขา B: 456 บาท
    """,
    tools=[bq_toolset],
)
