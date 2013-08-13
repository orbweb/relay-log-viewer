var data_columns = [
  {col_name: 'category', display_name: 'UID'},
  {col_name: 'human_data', display_name: 'Data (bytes)'}
];
var dataUsage = new Pie('#uid-data-chart', '#uid-data-data', data_columns, 'uid_data.json');

var data_columns = [
  {col_name: 'category', display_name: 'End Reason'},
  {col_name: 'human_data', display_name: 'Number'}
];
var dataUsage = new Pie('#end-reasons-chart', '#end-reasons-data', data_columns, 'end_reasons.json', 300, 300);
