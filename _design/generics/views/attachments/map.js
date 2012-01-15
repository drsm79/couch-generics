function(doc){
  if (doc._attachments){
    emit(null, doc._attachments);
  }
}
