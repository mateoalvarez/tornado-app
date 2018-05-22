function addAxesAndLegend (svg, xAxis, yAxis, margin, chartWidth, chartHeight) {
  var legendWidth  = 200,
      legendHeight = 100;

  // clipping to make sure nothing appears behind legend
  // svg.append('clipPath')
//     .attr('id', 'axes-clip')
//     .append('polygon')
//       .attr('points', (-margin.left)                 + ',' + (-margin.top)                 + ' ' +
//                       (chartWidth - legendWidth - 1) + ',' + (-margin.top)                 + ' ' +
//                       (chartWidth - legendWidth - 1) + ',' + legendHeight                  + ' ' +
//                       (chartWidth + margin.right)    + ',' + legendHeight                  + ' ' +
//                       (chartWidth + margin.right)    + ',' + (chartHeight + margin.bottom) + ' ' +
//                       (-margin.left)                 + ',' + (chartHeight + margin.bottom));

  var axes = svg.append('g')
    .attr('clip-path', 'url(#axes-clip)');

  axes.append('g')
    .attr('class', 'x axis')
    .attr('transform', 'translate(0,' + chartHeight + ')')
    .call(xAxis);

  axes.append('g')
    .attr('class', 'y axis')
    .call(yAxis)
    .append('text')
      .attr('transform', 'rotate(-90)')
      .attr('y', 6)
      .attr('dy', '.71em')
      .style('text-anchor', 'end')
      .text('Classfication');

}

function drawPaths (svg, data, x, y) {

  var medianLine = d3.svg.line()
    .interpolate('basis')
    .x(function (d) { return x(d.date); })
    .y(function (d) { return y(d.aggregated); });

  svg.datum(data);

  svg.append('path')
    .attr('class', 'median-line')
    .attr('d', medianLine)
    .attr('clip-path', 'url(#rect-clip)');
}

function startTransitions (svg, chartWidth, chartHeight, rectClip, x) {
  rectClip.transition()
    .duration(1000*10)
    .attr('width', chartWidth);
}

function makeChart (data) {
  var svgWidth  = 960,
      svgHeight = 500,
      margin = { top: 20, right: 20, bottom: 40, left: 40 },
      chartWidth  = svgWidth  - margin.left - margin.right,
      chartHeight = svgHeight - margin.top  - margin.bottom;
  console.log(data)
  var x = d3.time.scale().range([0, chartWidth])
            .domain(d3.extent(data, function (d) { return d.date; }));
      y = d3.scale.linear().range([chartHeight, 0])
            .domain([d3.min(data, function (d) { return d.aggregated; }), d3.max(data, function (d) { return d.aggregated; })]);

  var xAxis = d3.svg.axis().scale(x).orient('bottom').ticks(10)
                .innerTickSize(-chartHeight).outerTickSize(0).tickFormat(d3.time.format('%H:%M:%S')).tickPadding(10),
      yAxis = d3.svg.axis().scale(y).orient('left')
                .innerTickSize(-chartWidth).outerTickSize(0).tickPadding(10);

  var svg = d3.select('body').append('svg')
    .attr('width',  svgWidth)
    .attr('height', svgHeight)
    .append('g')
      .attr('transform', 'translate(' + margin.left + ',' + margin.top + ')');

  // clipping to start chart hidden and slide it in later
  var rectClip = svg.append('clipPath')
    .attr('id', 'rect-clip')
    .append('rect')
      .attr('width', 0)
      .attr('height', chartHeight);

  addAxesAndLegend(svg, xAxis, yAxis, margin, chartWidth, chartHeight);
  drawPaths(svg, data, x, y);
  startTransitions(svg, chartWidth, chartHeight, rectClip, x);

}
