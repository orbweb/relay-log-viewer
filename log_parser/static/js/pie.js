var Pie = function(pie_chart_id, pie_data_id, table_columns, data_url, width, height) {
  var width = width || 500;
  var height = height || 500;
  var radius = Math.min(width, height) / 2;

  var color = d3.scale.category20();

  var arc = d3.svg.arc()
      .outerRadius(radius - 10)
      .innerRadius(radius/3);

  var pie = d3.layout.pie()
      .sort(function(d1, d2) { return d2.data - d1.data; })
      .value(function(d) { return d.data; });

  var chart = d3.select(pie_chart_id).append('svg')
      .attr('width', width)
      .attr('height', height)
      .append('g')
      .attr('transform', 'translate(' + width / 2 + ',' + height / 2 + ')');

  var _that = this;

  var getData = function(querystring, callback) {
    var querystring = querystring || '';
    d3.json(data_url + '?' + querystring, function(error, ret_data) {
      var data = ret_data;
      data.forEach(function(d) {
        d.data = +d.data;
        // comma separate really long numbers
        d.human_data = Math.floor(d.data)
          .toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
      });
      if (callback) {
        callback(data);
      }
    });
  };

  this.draw = function (querystring) {
    getData(querystring, function(data) {
      var pie_data = d3.select(pie_data_id);

      // helper methods for highlighting the table rows and changing the
      // colors of the paths
      var highlightElement = function(d) {
        var slice = chart.select(pie_chart_id + ' #' + d.category);
        var color = d3.rgb(slice.style('fill'));
        slice.style('fill', color.darker(0.35))
          .attr('d', arc.outerRadius(radius));

        var text = pie_data.selectAll(pie_data_id + ' #' + d.category)
          .style('background', '#F5F5F5');
      };
      var unhighlightElement = function(d) {
        var slice = chart.select(pie_chart_id + ' #' + d.category);
        var color = d3.rgb(slice.style('fill'));
        slice.style('fill', color.brighter(0.35))
          .attr('d', arc.outerRadius(radius-10));

        var text = pie_data.selectAll(pie_data_id + ' #' + d.category)
          .style('background', '#FFF');
      };

      // handle pie chart
      var path = chart.selectAll('path')
        .data(pie(data), function(d) { return d.data.category + d.data.data; });
      path.enter().append('path')
          .attr('d', arc)
          .style('fill', function(d) { return color(d.data.category); })
          .attr('id', function(d) { return d.data.category; })
          .on('mouseover', function(d) { highlightElement(d.data); })
          .on('mouseout', function(d) { unhighlightElement(d.data); });
      path.exit().remove();

      // handle table
      var rows = pie_data.select('tbody').selectAll('tr')
        .data(data, function(d) { return d.category + d.data; });
      rows.enter().append('tr');
      rows.exit().remove();

      rows.attr('id', function(d) { return d.category; })
      .sort(function(d1, d2) { return d2.data - d1.data; })
      .on('mouseover', function(d) { highlightElement(d); })
      .on('mouseout', function(d) { unhighlightElement(d); });

      var columns = rows.selectAll('td')
        .data(function(data) {
          return table_columns.map(function(column) {
            return {column: column, value: data[column.col_name]};
          });
        })
        .enter().append('td')
        .text(function(d) { return d.value; });
    });
  };

  this.initialize = function(callback) {
    // add table headers
    var pie_data = d3.select(pie_data_id);
    pie_data.select('thead').append('tr')
      .selectAll('th')
      .data(table_columns)
      .enter().append('th')
      .text(function(col) { return col.display_name; });

    _that.draw('');
  };
};
