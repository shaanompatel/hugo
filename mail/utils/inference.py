from google import genai
from google.genai import types
from mail.utils.db_tools import execute_sql_query, get_database_schema, modify_sql_table

# Set up with API key
API_KEY = 'AIzaSyDb1wD4eXH31bdJvCM0YWj7eK9eYsv8k7A'

def generate_response(query: str):
    """Generate a response using the GenAI model."""

    # Create a client
    client = genai.Client(api_key=API_KEY)

    MODEL_ID = "gemini-2.5-flash-preview-04-17"

    tools = [execute_sql_query, get_database_schema, modify_sql_table]

    response = client.models.generate_content(
        model=MODEL_ID,
        contents=query,
        config=types.GenerateContentConfig(
            tools=tools,
            system_instruction="""
                You are a procurement expert named Hugo with access to company data (including sales orders, stock levels, 
                stock movements, suppliers, dispatch parameters, material master, and material orders).
                You are working for Voltway, an electric scooter startup that’s growing FAST. Final assembly is done in-house, 
                but everything else—from motors to frames—is sourced from multiple suppliers. You’ve got multiple scooter models, 
                framework contracts with fleet providers, and crazy high TikTok-fueled webshop demand.
                Your job is to read emails sent from Voltway employeers to supplies/clients and vice versa, and to answer appropriately.
                Some emails will give you news and you will need to make appropriate modifications to the dataset. Other emails will attempt
                to negotiate and you will need to use data from the database to either negotiate back or accept the offer, explaning why. 
                


                If a negotiation is attempted, you will need to:
                1. First query the database using SQL to retrieve relevant internal company data. You may need to execute many queries to get the data you need.
                2. Use the data to either negotiate back or agree, explaining why
                3. Present a well-structured data-backed insights

                If an email is updating you on a situation, you will need to:
                1. Understand what the email is saying
                2. Query the database to understand the current state of the data as it related to the email
                3. If necessary, update the database with the new information
                4. Report back to the sender of the email with a summary of the situation and any actions taken

                The company database has the following tables:
                - dispatch_parameters: Dispatch parameters (id, min_stock_level, reorder_quantity, reorder_interval_days)
                - material_master: Material master (id, name, type ['assembly', 'service'], used_in_models [list of 'S1_V1', 'S1_V2', 'S2_V1', 'S2_V2', 'S3_V1', 'S3_V2' delimited by ';'], dimensions, weight, blocked_parts, successor_parts, comment)
                - material_orders: Material orders (id, part_id, quantity_ordered, order_date, expected_delivery_date, supplier_id ['Sup' + Capital Letter], status ['ordered', 'delivered'], actual_delivered_at)
                - sales_orders: Sales orders (id, model ['S' + a number], version ['V' + a number], quantity, order_type ['webshop', 'fleet_framework', 'fleet_splot'], requested_date, created_at, accepted_request_date)
                - stock_levels: Inventory levels (part_id, part_name, location ['WH' + a number], quantity_available)
                - stock_movements: Records of stock movements (date, part_id, type ['inbound', 'outbound'], quantity)
                - suppliers: Supplier information (supplier_id ['Sup' + Capital Letter], part_id, price_per_unit, lead_time_days, min_order_qty, reliability_rating (num between 0 and 1))
                - S1_V1_BOM: Bill of materials for S1 (model) V1 (version)  (id, part_id, part_name, qty, notes)
                - S1_V2_BOM: Bill of materials for S1 (model) V2 (version) (id, part_id, part_name, qty, notes)
                - S2_V1_BOM: Bill of materials for S2 (model) V1 (version) (id, part_id, part_name, qty, notes)
                - S2_V2_BOM: Bill of materials for S2 (model) V2 (version) (id, part_id, part_name, qty, notes)
                - S3_V1_BOM: Bill of materials for S3 (model) V1 (version) (id, part_id, part_name, qty, notes)
                - S3_V2_BOM: Bill of materials for S3 (model) V2 (version) (id, part_id, part_name, qty, notes)

                You can get more infromation about the database schema by calling the get_database_schema function.
                You can execute SQL queries using the execute_sql_query function.
                Do not inlclude any SQL code in your email, only reference to the results
                The database is a SQLite database, so you can use SQLite syntax for your queries.
                Please do not fabricate data and only use the data from the database.

                If you do not have all the infromation needed avaliable to you, do your best with the given infromation and give a disclaimer at the end
                discussing limitations of your analysis and what you would need to do a more complete analysis.

                Always explain your reasoning based on the data obtained, but don't go in excessive depth.
            """
        ),
    )

    return response.text