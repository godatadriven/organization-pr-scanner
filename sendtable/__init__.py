import azure.functions as func

from sendtable.monthly_pr_table import image_bytes_to_buffer, send_monthly_pr_table


def main(tableBlob: func.InputStream) -> None:
    table_buffer = image_bytes_to_buffer(tableBlob.read())
    send_monthly_pr_table(table_buffer)
