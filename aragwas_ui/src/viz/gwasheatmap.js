import * as d3 from "d3";
import {schemeYlOrRd, interpolateYlOrRd} from "d3-scale-chromatic";
import _ from "lodash";

export default function gwasHeatmap() {
    var svg;
    var size = [800, 1000];
    var data;
    var scoreRange;
    var minScoreToDisplay = 0;
    var orientation = "horizontal";
    var xScale = d3.local();
    var histogramScale = d3.local();

    var yScale;
    var padding = 50;
    var margin = { "top": 10, "bottom": 75, "left": 180, "right": 80 };
    var transitionDuration = 150;
    var colorScale = d3.scaleQuantile();
    var fillScale = d3.scaleLinear().clamp(true);
    var histogramHeight = 100;
    var cellSize = 12;
    var legendElementWidth = cellSize * 2.5;
    var legendHeight = 75;
    var zoomRectBeginning = 0;
    var zoomBeginning = 0;
    var zoomChromosome = 0;
    var zoomEnd = 0;
    var zoombar;
    var selectedscatterplot;
    var isClick = false;
    var delay = 300;
    var clickedSnp;

    var draw, ticks, changeSize;

    function getScatterPlotTop() {
        return histogramHeight + margin.top;
    }

    function getPlotWidth() {
        return size[0] - margin.left - margin.right;
    }

    function getChromosomeWidth() {
        return getPlotWidth() / data.data.length;
    }

    function getPlotHeight() {
        return size[1] - margin.bottom - margin.top - histogramHeight - legendHeight;
    }

    function getDataPointSize(d) {
        return 2.5;
    }

    function ticks(n) {
        return Math.floor(getChromosomeWidth() / n);
    }

    function initData() {
        scoreRange = data.scoreRange;
        //var midPoint = scoreRange[1] - scoreRange[0] / 2;
        let values = _.flatten(_.flatten(data.data.map(d => d.data) )).map(d => d.score);
        colorScale.domain(values).range(schemeYlOrRd[9]);
        fillScale.domain(scoreRange);
        if (data.type === "top") {
            yScale = d3.scalePoint().domain(data.studies.map(function(d) { return d.name + " (" + d.id + ")"; }));
        }
    }

    function dontClick() {
        isClick = false;
    }

    function mouseover(p, ix) {
        var studyIdx = parseInt(this.parentNode.dataset.index);
        d3.selectAll(".y.axis text").filter(function(d, i) { return i === studyIdx; }).style("fill", "red");
        d3.select(this).attr("r", function(d) { return getDataPointSize() * 1.5; });
        svg.dispatch("highlightassociation", { detail: {associations: {position: p.pos, score: p.score, study: studyIdx}, event: d3.event} });
    }

    function onSnpClicked(d, chromosome) {
        svg.dispatch("clicksnp", { detail: {associations: [d], chromosome: chromosome, event: d3.event} });
    }


    function mouseout(p, ix) {
        d3.selectAll("text").classed("active", false);
        var studyIdx = parseInt(this.parentNode.dataset.index);
        d3.selectAll(".y.axis text").filter(function(d, i) { return i === studyIdx; }).style("fill", "#000");
        d3.select(this).attr("r", getDataPointSize);
        svg.dispatch("unhighlightassociation", { detail: {associations: [p], event: d3.event} });
    }

    function mousedown(d) {
        var m = d3.mouse(this);
        var dd;
        if (d.chr){
            dd = d;
        } else {
            isClick = true;
            clickedSnp = d;
            setTimeout(dontClick, delay);
            // this is for when the user starts by clicking on an association
            dd = this.parentNode.parentNode.__data__;
        }
        zoomChromosome = parseInt(dd.chr[3]);
        zoomRectBeginning = m[0];

        // pick up initial position & chromosome
        var range = [0, getChromosomeWidth() - padding];
        xScale.get(this).domain(dd.region).range(range);
        zoomBeginning = parseInt(Math.round(xScale.get(this).invert(m[0])));
        zoombar = svg.select("g#"+dd.chr+".chr").select("g.scatterplot")
            .append("rect")
            .attr("id", "zoombar")
            .style("fill", "grey").style("fill-opacity","0.2")
            .attr("x", m[0])
            .attr("width", 0)
            .attr("y", -5)
            .attr("height", getPlotHeight()+10);

        selectedscatterplot = svg.select("g#"+dd.chr+".chr").select("g.scatterplot");
        selectedscatterplot.on("mousemove", mousemove);
        selectedscatterplot.on("mouseup", mouseup);

    }
    function mousemove() {
        var m = d3.mouse(this);
        if (m[0] < zoomRectBeginning) {
            zoombar.attr("x", m[0]).attr("width", zoomRectBeginning-m[0]);
        } else {
            zoombar.attr("width", m[0]-zoomRectBeginning);
        }
    }

    function mouseup() {
        selectedscatterplot.on("mousemove", null);
        var m = d3.mouse(this);
        if (isClick){
            onSnpClicked(clickedSnp, zoomChromosome)
        } else {
            if (m[0] < zoomRectBeginning) {
                zoomBeginning = parseInt(Math.round(xScale.get(this).invert(m[0])));
                zoomEnd = parseInt(Math.round(xScale.get(this).invert(zoomRectBeginning)));
            } else {
                zoomEnd = parseInt(Math.round(xScale.get(this).invert(m[0])));
            }
            if (zoomEnd != zoomBeginning) {
                console.log("Zoom beginning: "+zoomBeginning+", zoom end: "+zoomEnd);
                // pick up final position (or min/max) and push to next view
                svg.dispatch("zoomin", { detail: {range: [zoomBeginning,zoomEnd],chromosome:zoomChromosome, event: d3.event} });
            }
        }
    }

    function chart(selection) {

        function drawCell(row) {
            var cell = d3.select(this).selectAll(".cell")
                .data(row, function(d) { return d.pos; })
                .enter().append("circle")
                .attr("class", "cell")
                .attr("cx", function(d) { return xScale.get(this)(d.pos); })
                .attr("cy", function(d, i) { return yScale(i); })
                .attr("r", getDataPointSize)
                //.style("fill-opacity", function(d) { return fillScale(d.score); })
                .style("fill", function(d) { return colorScale(d.score); })
                .on("mouseover", mouseover)
                .on("click", onSnpClicked)
                .on("mouseout", mouseout)
                .on("mousedown", mousedown);
        }

        draw = function() {
            changeSize();

            drawAxes();
            drawPoints();
            drawHistograms();
            drawLegend();

            var legend = svg.selectAll(".legend");
            legend.append("text")
                .text("Scores")
                .attr("id", "scores")
                .attr("x", legendElementWidth * 4)
                .attr("y", (cellSize * 3))
                .style("font-size", 10);
        };
        changeSize = function() {
            svg.selectAll("g.chr")
                .attr("transform", function(d, i) {
                    return "translate(" + (margin.left + i * getChromosomeWidth()) + ",0)";
                })
                .each(function(d) {
                    var range = [0, getChromosomeWidth() - padding];
                    var histogram = histogramScale.get(this);
                    histogram.x.domain(d.bins.map(function(b, ix) { return ix; })).range(range);
                    histogram.y.domain(d3.extent(d.bins)).range([histogramHeight, 0]);
                    xScale.get(this).domain(d.region).range(range);
                });
        };

        function drawLegend() {
            var legend = svg.selectAll(".legend")
                .attr("transform", "translate(" + getPlotWidth() / 2  + "," + (size[1] - margin.bottom / 2) + ")")
                .selectAll(".legendItem")
                .data(schemeYlOrRd[9])
                .enter().append("g")
                .attr("class", "legendItem");

            legend.append("rect")
                .attr("x", function(d, i) { return legendElementWidth * i; })
                .attr("y", 0)
                .attr("width", legendElementWidth)
                .attr("height", cellSize)
                .style("fill", function(d, i) { return d; });

            legend.append("text")
                .text(function(d) {
                    var extend  = colorScale.invertExtent(d);
                    return Math.round(10*extend[0])/10;
                 })
                .attr("id", "legendvalues")
                .attr("x", function(d, i) { return legendElementWidth * i; })
                .attr("y", (cellSize * 2))
                .style("font-size", 10);
        }

        function drawHistograms() {
            var bars = svg.selectAll("g.chr")
                .selectAll("g.histogram").selectAll("rect.bar").data(function(d) { return d.bins; });
            bars.exit().remove();
            bars.enter()
                .append("rect")
                .style("fill", "steelblue")
                .merge(bars)
                .attr("x", function(d, i) { return histogramScale.get(this).x(i); })
                .attr("width", function(d) { return histogramScale.get(this).x.bandwidth(); })
                .attr("y", function(d) { return histogramScale.get(this).y(d); })
                .attr("height", function(d) { return histogramHeight - histogramScale.get(this).y(d); });
        }

        function drawPoints() {
            var row = svg.selectAll("g.chr").selectAll("g.scatterplot")
                .selectAll("g.row")
                .data(function(d, i) { return d.data; }, function(d) { return d.pos; });

            row.exit().remove();
            row.enter().append("g")
                .attr("class", "row")
                .attr("data-index", function(d, ix) { return ix; })
                .attr("transform", function(d, i) { return "translate(0," + yScale(data.studies[i].name + " (" + data.studies[i].id + ")") + ")"; })
                .each(drawCell);
        }

        function drawAxes() {
            // Attribute the mousedown event on the scatterplot background
            svg.selectAll("g.chr").selectAll("g.scatterplot")
                .append("rect")
                .style("fill-opacity", "0")
                .attr("x", 0)
                .attr("width", getChromosomeWidth() - padding)
                .attr("y", -5)
                .attr("height", getPlotHeight()+10)
                .on("mousedown",mousedown)
                .on("contextmenu", function(d,i){
                    d3.event.preventDefault();
                    svg.dispatch("dezoom");
                });

            yScale.range([0, getPlotHeight()]);
            svg.selectAll("g.x.axis")
                .attr("transform", function(d) {
                    return "translate(0," + (getPlotHeight() + getScatterPlotTop() + margin.top) + ")";
                })
                .transition().duration(transitionDuration)
                .each(function(d) {
                    if (d.region[1]-d.region[0]>1e6){
                        d3.axisBottom(xScale.get(this)).ticks(ticks(40)).tickFormat(d3.formatPrefix(".1", 1e6))(d3.select(this));
                    } else {
                        d3.axisBottom(xScale.get(this)).ticks(ticks(80))(d3.select(this));
                    }

                });

            svg.selectAll(".xaxislabel")
                .attr("x", getChromosomeWidth() / 2 - 71)
                .attr("y", (getPlotHeight() + getScatterPlotTop() + margin.top + margin.bottom  ));


            svg.select("g.y.axis")
                .transition().duration(transitionDuration)
                .call(d3.axisLeft(yScale))

        }

        selection.each(function(dt) {
            d3.selectAll("svg > *").remove(); // used when zooming
            d3.select("svg").node().oncontextmenu = function(){svg.dispatch("dezoom"); return false;}; //prevent contextmenu in Chrome
            svg = d3.select(this);
            data = dt;
            initData();

            svg.append("g")
                .attr("class", "y axis")
                .attr("transform", "translate(" + margin.left + "," + getScatterPlotTop() + ")")
                .call(d3.axisLeft(yScale));

            svg.append("g")
                .attr("class", "legend");

            var chromGroups = svg.selectAll("g.chr")
                .data(data.data, function(d) { return d.chr; });

            chromGroups.exit().remove();

            var chromGroupsEntered = chromGroups.enter()
                .append("g")
                .attr("class", "chr")
                .attr("id", function(d) { return d.chr; })
                .each(function(d) {
                    histogramScale.set(this, { x: d3.scaleBand(), y: d3.scaleLinear() });
                    xScale.set(this, d3.scaleLinear());
                });

            chromGroupsEntered
                .append("g")
                .attr("class", "x axis")
                .call(function(d) { d3.axisBottom(xScale.get(d.node()))(d); });

            chromGroupsEntered
                .append("text")
                .attr("class", "xaxislabel")
                .text(function(d) { if(d.region[1]-d.region[0]>1e6){return d.chr + " (Mbp)";} else {return d.chr;}});


            chromGroupsEntered
                .append("g")
                .attr("class", "scatterplot")
                .attr("transform", "translate(0, " + getScatterPlotTop() + ")");

            chromGroupsEntered
                .append("g")
                .attr("class", "histogram");

            chromGroups = chromGroupsEntered.merge(chromGroups);

            draw();
        });
    }

    chart.size = function(value) {
        if (!arguments.length) {
            return size;
        }
        size = value;
        if (typeof draw === "function") {
            changeSize();
        }
    };

    return chart;
}
