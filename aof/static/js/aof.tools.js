function getGridData(jsonObj) {
	dataArray = [];
	headerArray = [];
	
	for(var i = 0; i <  jsonObj.head.vars.length; i++) {
		headerArray[i] =  {headerText: jsonObj.head.vars[i]};
	}
	
	for(var i = 0; i < jsonObj.results.bindings.length; i++) {
		dataArray[i] = [];
		for (var v in jsonObj.head.vars) {
		    console.log(jsonObj.head.vars[v])
		    var key = jsonObj.head.vars[v];
		    if (key in jsonObj.results.bindings[i]) {
		      console.log(jsonObj.results.bindings[i][key].value)
		      dataArray[i].push(jsonObj.results.bindings[i][key].value);
		    }
		    else {
		      dataArray[i].push("");
		    }
		}
	} 
	
	for(var i = 0; i <  jsonObj.head.vars.length; i++) {
		headerArray[i] =  {headerText: jsonObj.head.vars[i]};
	}
	
	return [headerArray, dataArray]
} 