var width = 500,
    height = 500,
    radius = Math.min(width, height) / 2;

var tableColumns = [
  {col_name: 'uid', display_name: 'UID'},
  {col_name: 'human_data', display_name: 'Data (megabytes)'}
];

var color = d3.scale.category20();

var arc = d3.svg.arc()
    .outerRadius(radius - 10)
    .innerRadius(radius/3);

var pie = d3.layout.pie()
    .sort(function(d1, d2) { return d2.data - d1.data; })
    .value(function(d) { return d.data; });

var svg = d3.select('#pie-chart').append('svg')
    .attr('width', width)
    .attr('height', height)
    .append('g')
    .attr('transform', 'translate(' + width / 2 + ',' + height / 2 + ')');

var pie_data = d3.select('#pie-data');

d3.json('pie.json', function(error, data) {

  data.forEach(function(d) {
    d.data = +d.data;
    d.human_data = Math.floor(d.data/1000)
      .toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
  });

  var g = svg.selectAll('.arc')
      .data(pie(data))
    .enter().append('g')
      .attr('class', 'arc');

  g.append('path')
      .attr('d', arc)
      .style('fill', function(d) { return color(d.data.uid); })
      .attr('id', function(d) { return d.data.uid; })
      .on('mouseover', function(d) { highlightElement(d.data); })
      .on('mouseout', function(d) { unhighlightElement(d.data); });

  // add table headers
  pie_data.select('thead').append('tr')
    .selectAll('th')
    .data(tableColumns)
    .enter().append('th')
    .text(function(col) { return col.display_name; });

  var rows = pie_data.select('tbody').selectAll('tr')
    .data(data)
    .enter().append('tr');

  rows.attr('id', function(d) { return d.uid; })
  .sort(function(d1, d2) { return d2.data - d1.data; })
  .on('mouseover', function(d) { highlightElement(d); })
  .on('mouseout', function(d) { unhighlightElement(d); });

  var columns = rows.selectAll('td')
    .data(function(data) {
      return tableColumns.map(function(column) {
        return {column: column, value: data[column.col_name]};
      });
    })
    .enter().append('td')
    .text(function(d) { return d.value; });

  var highlightElement = function(d) {
    var slice = svg.select('#pie-chart #' + d.uid);
    var color = d3.rgb(slice.style('fill'));
    slice.style('fill', color.darker(0.35))
      .attr('d', arc.outerRadius(radius));

    var text = pie_data.selectAll('#pie-data #' + d.uid)
      .style('background', '#F5F5F5');
  };

  var unhighlightElement = function(d) {
    var slice = svg.select('#pie-chart #' + d.uid);
    var color = d3.rgb(slice.style('fill'));
    slice.style('fill', color.brighter(0.35))
      .attr('d', arc.outerRadius(radius-10));

    var text = pie_data.selectAll('#pie-data #' + d.uid)
      .style('background', '#FFF');
  };

});
