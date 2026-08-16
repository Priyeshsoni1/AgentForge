def execute_tool_safely(tool_name,arguments,execute_tool):
    try:
        result=execute_tool(tool_name,arguments)
        return {
            "success":True,
            "result":result,
        }
    except Exception as e:
        return {
            "success":False,
            "error":str(e),
        }