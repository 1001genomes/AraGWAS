import * as d3 from "d3";
import laneLayout from "../viz/lanelayout.js";

export default function() {
    var triangleSize = 20;
    var cdsScaler = 2;
    var geneScaler = 6;
    var utrScaler = 3;
    var xAxis = null;
    var selectionLine = null;
    var selectionLineLabel = null;
    var highlightPos = null;
    var svg = null;
    var trackElem = null;
    var region = [];
    var isoforms;
    var draw;
    var updateSelectionLine;
    var updateRegion;
    var timelineBands;
    var size = [1000, 250];
    var margin =  { top: 20, bottom: 20} ;

    var timelineSize = function() {
        return [size[0], size[1] - margin.bottom - margin.top];
    };

    var timeline = laneLayout()
        .size(timelineSize())
        .padding(20)
        .maxBandHeight(50)
        .gap(12)
        .bandStart(function(d) { return d.positions.gte; })
        .bandEnd(function(d) { return d.positions.lte; })
        .dateFormat(function(d) { return parseInt(d); });

    var triangle = d3.symbol()
        .type(d3.symbolTriangle)
        .size(triangleSize);

    var positionTriangle = function(d) {
        var rotation = 0;
        var xPos = 0;
        if (d.strand === "-") {
            rotation = -90;
            xPos = -Math.sqrt(triangleSize) / 2;
        } else {
            rotation = 90;
            xPos = (d.end - d.start) + Math.sqrt(triangleSize) / 2;
        }
        var yPosScaler = Math.round((geneScaler / cdsScaler) + 1);
        return "translate(" + xPos + "," + d.dy / yPosScaler + ") rotate(" + rotation + ")";
    };

    var positionFeature = function(d) {
        var parentData = d3.select(this.parentNode).datum();
        return scale(d.positions.gte) - parentData.start;
    };

    var positionUtrFeatures = function(d) {
        return "translate(0," + d.dy * ((1 / cdsScaler - 1 / utrScaler) / 2) + ")";
    };

    var scale = function(value) {
        return timeline.displayScale()(value);
    };

    var invert = function(value) {
        return timeline.displayScale().invert(value);
    };

    var onMouseMove = function(d, i) {
        var pos = d3.mouse(this);
        highlightPos = invert(pos[0]);
        updateSelectionLine();
    };

    function chart(selection) {
        selection.each(function(data) {
            isoforms = data;
            draw = function() {
                timelineBands = timeline(isoforms);

                svg.select("g.axis.x").call(xAxis);
                svg.select("#clip-rect")
                    .attr("width", size[0])
                    .attr("height", size[1]);

                var isoformGroup = trackElem.selectAll("g.isoform")
                    .data(timelineBands, function(d) { return d.name; });

                isoformGroup.exit().remove();

                // draw isoform groups
                var newIsoForms = isoformGroup.enter()
                    .append("g")
                    .attr("class", "isoform")
                    .style("pointer-events", "all")
                    .on("mouseover", function(d, i) {
                        svg.dispatch("highlightgene", { detail: {gene: d, event: d3.event} });
                    })
                    .on("mouseout", function(d, i) {
                        svg.dispatch("unhighlightgene", { detail: {gene: d, event: d3.event} });
                    });

                // draw text
                newIsoForms
                    .append("text")
                    .attr("fill", "black");

                // draw gene line
                newIsoForms
                    .append("rect")
                    .attr("class", "gene");

                //draw triangle
                newIsoForms
                    .append("path")
                    .attr("class", "strand-triangle")
                    .attr("d", triangle)
                    .style("stroke", "black")
                    .style("fill", "black");

                //draw cds
                newIsoForms
                    .append("g")
                    .attr("class", "cds")
                    .selectAll("rect.cds")
                    .data(function(d) { return d.cds; })
                    .enter()
                    .append("rect")
                    .attr("class", "cds")
                    .style("fill", "#FF8100");

                newIsoForms
                    .append("g")
                    .attr("class", "fivePrime_UTR")
                    .selectAll("rect.fivePrime_UTR")
                    .data(function(d) { return d.fivePrime_UTR; })
                    .enter()
                    .append("rect")
                    .attr("class", "fivePrime_UTR")
                    .style("fill", "#ABF000");

                newIsoForms
                    .append("g")
                    .attr("class", "threePrime_UTR")
                    .selectAll("rect.threePrime_UTR")
                    .data(function(d) { return d.threePrime_UTR; })
                    .enter()
                    .append("rect")
                    .attr("class", "threePrime_UTR")
                    .style("fill", "#00BD39");

                var allIsoForms = isoformGroup.merge(newIsoForms);

                allIsoForms
                    .attr("transform", function(d) { return "translate(" + d.start + "," + d.y + ")"; });

                allIsoForms.select("text")
                    .attr("transform", function(d) { return "translate(0," + d.dy / (cdsScaler / 2) + ")"; })
                    .text(function(d) { return d.name; });

                allIsoForms.select("rect.gene")
                    .attr("y", function(d) { return d.dy * ((1 / cdsScaler - 1 / geneScaler) / 2); })
                    .attr("height", function(d) { return d.dy / geneScaler; })
                    .attr("width", function(d) {return d.end - d.start; });

                allIsoForms.select("path.strand-triangle")
                    .attr("transform", positionTriangle);

                allIsoForms.select("g.cds")
                    .selectAll("rect.cds")
                    .attr("x", positionFeature)
                    .attr("width", function(d) { return scale(d.positions.lte) - scale(d.positions.gte); })
                    .attr("height", function(d) { return d3.select(this.parentNode).datum().dy / cdsScaler; });

                allIsoForms.select("g.fivePrime_UTR")
                    .attr("transform", positionUtrFeatures)
                    .selectAll("rect.fivePrime_UTR")
                    .attr("x", positionFeature)
                    .attr("width", function(d) { return scale(d.positions.lte) - scale(d.positions.gte); })
                    .attr("height", function(d) { return d3.select(this.parentNode).datum().dy / utrScaler; });

                allIsoForms.select("g.threePrime_UTR")
                    .attr("transform", positionUtrFeatures)
                    .selectAll("rect.threePrime_UTR")
                    .attr("x", positionFeature)
                    .attr("width", function(d) { return scale(d.positions.lte) - scale(d.positions.gte); })
                    .attr("height", function(d) { return d3.select(this.parentNode).datum().dy / utrScaler; });

                // update existing
                isoformGroup.attr("transform", function(d) { return "translate(" + d.start + "," + d.y + ")"; });

            };

            updateSelectionLine = function() {
                if (!highlightPos) {
                    return;
                }
                var xPos = scale(highlightPos);
                selectionLine.attr("x1", xPos);
                selectionLine.attr("x2", xPos);

                selectionLineLabel
                    .attr("x", xPos)
                    .text(Math.round(highlightPos));

                d3.selectAll("g.isoform.highlight")
                    .classed("highlight", false)
                    .selectAll("rect.highlight")
                    .classed("highlight", false);

                var isoforms = d3.selectAll("g.isoform")
                    .filter(function(d) {
                        return (d.originalEnd >= highlightPos && d.originalStart <= highlightPos);
                    });

                isoforms.classed("highlight", true);

                var features = isoforms
                .selectAll("rect.cds, rect.threePrime_UTR, rect.fivePrime_UTR").filter(function(d) {
                    return (d.positions.lte >= highlightPos && d.positions.gte <= highlightPos);
                });
                features.classed("highlight", true);
            };

            updateRegion = function() {
                timeline.extent(region);
                draw();
            };

            timeline.extent(region);
            svg = d3.select(this);
            svg.selectAll("*").remove();
            svg.on("mousemove", onMouseMove)
            .append("defs").append("svg:clipPath")
                .attr("id", "geneplot-clip")
                    .append("svg:rect")
                        .attr("id", "clip-rect")
                        .attr("x", "0")
                        .attr("y", "0")
                        .attr("width", size[0])
                        .attr("height", size[1]);


            xAxis = d3.axisBottom(timeline.displayScale());
            trackElem = svg.append("g")
                .attr("transform", "translate(0," + margin.top + ")")
                .attr("clip-path", "url(#geneplot-clip)");
            draw();

            svg.append("g")
                .attr("class", "x axis")
                .attr("transform", "translate(0," + (size[1] - margin.bottom) + ")")
                .call(xAxis);

            selectionLine = svg.append("line")
                .attr("class", "selection")
                .style("opacity", 1)
                .attr("y2", size[1] - margin.bottom)
                .attr("shape-rendering", "crispEdges")
                .attr("stroke-width", 2)
                .style("fill", "#007EFF")
                .style("pointer-events", "none")
                .style("stroke", "#007EFF");

            selectionLineLabel = svg.append("text")
                .attr("class", "selection")
                .attr("y", 12)
                .style("fill", "#007EFF")
                .style("pointer-events", "none");

            updateSelectionLine();
        });
    }

    chart.highlightPos = function(value) {
        if (!arguments.length) {
            return highlightPos;
        }
        highlightPos = value;
        if (typeof updateSelectionLine === "function") {
            updateSelectionLine();
        }
        return chart;
    };

    chart.size = function(value) {
        if (!arguments.length) {
            return size;
        }
        size = value;
        timeline.size(timelineSize());
        if (typeof draw === "function") {
            draw();
        }
    };

    chart.data = function(value) {
        if (!arguments.length) {
            return region;
        }
        isoforms = value;
        if (typeof draw === "function") {
            draw();
        }
        return chart;
    };

    chart.region = function(value) {
        if (!arguments.length) {
            return region;
        }
        region = value;
        if (typeof updateRegion === "function") {
            updateRegion();
        }
        return chart;
    };
    return chart;
}
