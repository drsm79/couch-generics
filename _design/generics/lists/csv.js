function(head, req) {
	var row;
	var first = true;
	while(row = getRow()) {
		var thing = [];
		if (first){
			thing.push('key');
			for (k in row.value) {
				thing.push(k);
			}
			send(thing.join(',') + '\n');
			first = false;
			thing = [];
		}
		thing.push(row.key);
		for (v in row.value){
			thing.push(row.value[v]);
		}
		send(thing.join(',') + '\n');
	}
}
		