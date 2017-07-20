import * as d3 from "d3";

export default function() {
    var svg;
    var margins = { top: 40, left: 40, bottom: 10, right: 40 };
    var axes = { x: null, y: null };
    var padding = 40;
    var options;
    var associations = [[0,0]];
    var size = [800, 300];
    var scales = { x: d3.scaleLinear(), y: d3.scaleLinear() };
    var transitionDuration = 750;
    var drawThreshold, drawAxes, drawPoints, draw, prepareData;

    var position = function(d) { return d[0]; };
    var score = function(d) {  return d[1]; };

    var getSnpColor = function(d) {
        var blue = 204 - options.chr * 40;
        var red = 51 + options.chr * 40;
        return "rgb(" + red + ",102," + blue + ")"
    };

    var positionSnp = function(d) {
        var xPos = scales.x(position(d));
        var yPos = scales.y(score(d));
        return "translate(" + xPos + "," + yPos + ")";
    };

    var getPlotWidth = function() { return size[0] - margins.left - margins.right; };
    var getPlotHeight = function() {
        var h = size[1] - margins.top;
        h -= margins.bottom;
        return h;
    };

    function onMouseOverSnp(d) {
        d.highlighted = true;
        d3.select(this).attr("r",6);
        d3.select(this).attr("opacity",0.5);
        svg.dispatch("highlightassociation", { detail: {associations: [d], event: d3.event} });
    }

    function onMouseOutSnp(d) {
        d.highlighted = false;
        d3.select(this).attr("r",2.5);
        d3.select(this).attr("opacity",1);
        svg.dispatch("unhighlightassociation", { detail: {associations: [d], event: d3.event} });
    }


    function chart(selection) {
        selection.each(function(data) {
            svg = d3.select(this);
            draw = function() {
                prepareData();
                drawAxes();
                drawPoints();
                drawThreshold();
            };

            drawAxes = function() {
                const h = getPlotHeight();
                const w = getPlotWidth();
                const len = Math.pow(10, ((String(Math.round(options.max_x / 5)).length - 1)));
                const valX = Math.round(options.max_x / 5 / len) * len;
                // draw graph help-lines in background
                for (var i = 0; (valX * i) < options.max_x ; i++) {
                    svg.append("svg:g")
                        .attr("transform", "translate(" + scales.x(valX * i) + "," + (h - padding / 1.5) + ")")
                        .append("text").text(valX * i)
                        .attr("text-anchor", "middle");
                }
                const valY = Math.round(options.max_y / 3);
                for (var i = 1; (i * valY) < (options.max_y + 1); i++) {
                    svg.append("svg:line")
                        .attr("x1", scales.x(0))
                        .attr("y1", scales.y(valY * i))
                        .attr("x2", scales.x(options.max_x))
                        .attr("y2", scales.y(valY * i))
                        .style("stroke", "#CCC")
                        .style("stroke-width", 1);
                    svg.append("svg:g")
                        .attr("transform", "translate(" + (padding / 1.5) + "," + scales.y(valY * i) + ")")
                        .append("text").text(valY * i)
                        .attr("text-anchor", "middle");
                }
                // write text-information to axis and draw graph-elements
                svg.append("svg:g")
                    .attr("transform", "translate(" + 5 + "," + 12 + ")")
                    .append("text").text("Manhattan-plot for chromosome "+options.chr)
                    .style("font-weight", "bold");
                svg.append("svg:g")
                    .attr("transform", "matrix(0, -1, 1, 0, 0, 0)").append("svg:g")
                    .attr("transform", "translate(" + ((padding - 0.85*h)) + "," + (padding / 3) + ")")
                    .append("text").text("-log10(p-value)");
                svg.append("svg:line")
                    .attr("x1", scales.x(0))
                    .attr("y1", scales.y(0))
                    .attr("x2", scales.x(options.max_x))
                    .attr("y2", scales.y(0))
                    .style("stroke", "#000000")
                    .style("stroke-width", 1);
                svg.append("svg:g")
                    .attr("transform", "translate(" + ((w - padding) / 2) + "," + (h - padding / 5) + ")")
                    .append("text").text("chromosomal position [bp]")
                    .attr("text-anchor", "middle");
                svg.append("rect")
                    .attr("x", padding)
                    .attr("y", padding / 1.6)
                    .attr("width", padding / 2.5)
                    .attr("height", padding / 3.5)
                    .style("fill", getSnpColor);
                svg.append("svg:g")
                    .attr("transform", "translate(" + (padding + 25) + "," + (padding / 1.1) + ")")
                    .append("text").text("-log10(p-value)");
                svg.append("rect")
                    .attr("x", padding * 4 + 25)
                    .attr("y", padding / 1.6)
                    .attr("width", padding / 2.5)
                    .attr("height", padding / 3.5)
                    .style("fill", "#F0001E");
                svg.append("svg:g")
                    .attr("transform", "translate(" + (padding * 4 + 50) + "," + (padding / 1.1) + ")")
                    .append("text").text("Bonferroni threshold [" + options.alpha + "]");
            };

            drawThreshold = function() {
                var d2 = [[0, options.bonferroniThreshold], [options.max_x, options.bonferroniThreshold]];
                svg.append("svg:line")
                    .attr("x1", scales.x(d2[0][0]))
                    .attr("y1", scales.y(d2[0][1]))
                    .attr("x2", scales.x(d2[1][0]))
                    .attr("y2", scales.y(d2[1][1]))
                    .style("stroke", "#F0001E")
                    .style("stroke-width", 1.5 );
            };

            drawPoints = function() {
                if(associations !== undefined){
                    var snps = svg.selectAll("circle")
                        .data(associations);

                    snps.exit()
                        .attr("transform", positionSnp)
                        .transition(d3.transition().duration(transitionDuration))
                        .attr("transform", function(d) { return "translate(" + scales.x(position(d)) + ",-100)"; })
                        .style("fill-opacity", 0)
                        .remove();

                    snps
                        .transition(d3.transition().duration(transitionDuration))
                        .attr("transform", positionSnp)
                        .attr("d", d3.symbol()
                            .type(d3.symbolCircle)
                            .size(2.5),
                        )
                        .style("stroke", getSnpColor)
                        .style("fill", getSnpColor);

                    snps.enter()
                        .append("circle")
                        // .attr("cx", function(d) { return scales.x(position(d))})
                        // .attr("cy", function(d) { return scales.y(score(d))})
                        .attr("r", 2.5)
                        .style("fill", getSnpColor)
                        .on("mouseover", onMouseOverSnp)
                        .on("mouseout", onMouseOutSnp)
                        .style("fill-opacity", 1)
                        // .transition(d3.transition().duration(transitionDuration))
                        .attr("transform", positionSnp);
                }
            };
            prepareData = function() {
                scales.x.domain([0, options.max_x]).range([padding, getPlotWidth()-padding]);
                scales.y.domain([0, options.max_y + 1]).range([getPlotHeight()-padding, margins.top]);
            };

            if (data !== undefined){
                associations = data;
            } else {
                associations = [0];
            }
            // prepate data
            prepareData();


            drawThreshold();

        });
    }

    chart.size = function(value) {
        if (!arguments.length) {
            return size;
        }
        size = value;
        scales.x.range([padding, getPlotWidth()-padding]);
        scales.y.range([getPlotHeight()-padding, margins.top]);
        if (typeof draw === "function") {
            draw();
        }
        return chart;
    };
    chart.data = function(value) {
        if (!arguments.length) {
            return region;
        }
        associations = value;
        if (typeof draw === "function") {
            draw();
        }
        return chart;
    };

    chart.options = function(value) {
        if (!arguments.length) {
            return options;
        }
        options = value;
        if (typeof draw === "function") {
            draw();
        }
        return chart;
    };
    chart.clear = function() {
        if (svg){
            svg.selectAll("g").remove();
            svg.selectAll("line").remove();
            svg.selectAll("circle").remove();
        }
    };

    return chart;
}
