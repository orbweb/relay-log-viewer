var getVals = function(curr_scope) {
  var params = {};
  var selects = curr_scope.parent().find('select');
  selects.each(function(i, select) {
    params[select.id] = select.value;
  });
  return params;
};

var data_columns = [
  {col_name: 'category', display_name: 'UID'},
  {col_name: 'human_data', display_name: 'Data (bytes)'}
];
var data_usage = new Pie('#uid-data-chart', '#uid-data-data', data_columns, '/view/charts/uid_data.json');
data_usage.initialize();

var data_columns = [
  {col_name: 'category', display_name: 'End Reason'},
  {col_name: 'human_data', display_name: 'Number'}
];
var end_reasons = new Pie('#end-reasons-chart', '#end-reasons-data', data_columns, '/view/charts/end_reasons.json', 300, 300);
end_reasons.initialize();

var data_columns = [
  {col_name: 'category', display_name: 'Connection Type'},
  {col_name: 'human_data', display_name: 'Number'}
];
var relay_p2p_counts = new Pie('#relay-p2p-chart', '#relay-p2p-data', data_columns, '/view/charts/relay_p2p_counts.json', 300, 300);
relay_p2p_counts.initialize();
$('select#month').change(function(obj) {
  relay_p2p_counts.draw($.param(getVals($(this))));
});
$('select#year').change(function(obj) {
  relay_p2p_counts.draw($.param(getVals($(this))));
});
$('select#month').prop('selectedIndex', -1);
