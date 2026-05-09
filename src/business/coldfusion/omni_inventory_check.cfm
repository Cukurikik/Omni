<!--- OMNI Legacy Business Bridge: ColdFusion --->
<cfset RequestData = GetHttpRequestData()>
<cfif RequestData.method EQ "POST">
    <cfset InputData = DeserializeJSON(RequestData.content)>
    <cfset sku = InputData.sku>
    
    <!--- Query simulated Database --->
    <cfquery name="GetStock" datasource="OmniLegacyDB">
        SELECT StockLevel FROM Inventory WHERE SKU = <cfqueryparam value="#sku#" cfsqltype="cf_sql_varchar">
    </cfquery>
    
    <cfset response = StructNew()>
    <cfif GetStock.RecordCount GT 0>
        <cfset response.status = "success">
        <cfset response.stock = GetStock.StockLevel>
    <cfelse>
        <cfset response.status = "error">
        <cfset response.message = "SKU not found in OMNI CF Bridge">
    </cfif>
    
    <cfcontent type="application/json">
    <cfoutput>#SerializeJSON(response)#</cfoutput>
<cfelse>
    <cfheader statuscode="405" statustext="Method Not Allowed">
</cfif>
