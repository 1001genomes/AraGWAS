import * as d3 from "d3";
import {schemeRdYlBu,  interpolateRdYlBu} from "d3-scale-chromatic";
import _ from "lodash";

export default function() {
    var svg;
    var data;
    var size = [300, 300];
    var colorBandScale;
    var sizeOfColorLegendBox = 18;
    var sizeOfColorBand = 25;
    var margin = 3;
    var numberOfLegendItemsPerCol;
    var numberOfColumns;
    var maxNumberOfColorLegendBoxesPerColumn;
    var legendTypes;
    var overrideColors = d3.map([]);
    var legendsToInclude = null;
    var legendMap;
    var activeLegendType = {name: "", isNumber: true};
    var gradient;
    var colorsForScale = ["steelblue"];
    var colorScale = d3.scaleOrdinal().range(colorsForScale);
    var draw;
    var event = d3.dispatch("highlightlegend", "unhighlightlegend");

    function getLegendItemBoxSize() {
        return sizeOfColorLegendBox - 2 * margin;
    }

    function getPlotHeight() {
        return size[1] - 30 ;
    }

    function hasOneColumn() {
        return numberOfColumns <= 1;
    }

    function calculateGrid() {
        var numberOfLegendItems = colorScale.domain().length;
        maxNumberOfColorLegendBoxesPerColumn = getPlotHeight() / sizeOfColorLegendBox;
        numberOfColumns = Math.ceil(numberOfLegendItems / maxNumberOfColorLegendBoxesPerColumn);
        numberOfLegendItemsPerCol = Math.round(numberOfLegendItems / numberOfColumns);
    }

    function positionLegendItem(d, i) {
        var column = (Math.floor(i / maxNumberOfColorLegendBoxesPerColumn));
        return "translate(" + (column * sizeOfColorLegendBox) + "," + (i - maxNumberOfColorLegendBoxesPerColumn * column) * sizeOfColorLegendBox + ")";
    }

    function initLegend() {
        var filterMap = d3.set([]);
        var sampleEntry = d3.map(data[0]);
        legendTypes = [{ "name": "", "isNumber": true }];
        if (legendsToInclude && legendsToInclude.length > 0) {
            for (var i = 0; i < legendsToInclude.length; i++) {
                var legendToInclude = legendsToInclude[i];
                var prop = _.get(sampleEntry, legendToInclude);
                legendTypes.push({name: legendToInclude, isNumber: !isNaN(prop)});
            }
        } else {
            sampleEntry = d3.map(data[0]);
            legendTypes = legendTypes.concat(d3.set(
                sampleEntry
                .keys()
                .filter(function(d) {
                    return !filterMap.has(d);
                }),
            ).values().map(function(d) { return {name: d, isNumber: !isNaN(sampleEntry.get(d))}; }));
        }
        if (!activeLegendType) {
            activeLegendType = legendTypes[0];
        }
        initScales();
    }

    function linspace(start, end, n) {
        var out = [];
        var delta = (end - start) / (n - 1);

        var i = 0;
        while (i < (n - 1)) {
            out.push(start + (i * delta));
            i++;
        }

        out.push(end);
        return out;
    }

    function initScales() {
        legendMap = d3.nest().key(function(d) {return _.get(d, activeLegendType.name); }).map(data, d3.map);
        var legendItems = legendMap.keys();
        var numOfLegendItems = legendItems.length;
        if (!activeLegendType.isNumber) {
            colorScale = d3.scaleOrdinal().domain(legendItems);
            if (overrideColors.has(activeLegendType.name)) {
                colorScale.range(overrideColors[activeLegendType.name]);
            } else {
                if (numOfLegendItems <= 10) {
                    colorScale.range(d3.schemeCategory10);
                } else if (numOfLegendItems <= 20) {
                    colorScale.range(d3.schemeCategory20c);
                } else {
                    colorScale.range(colors60);
                }
            }
            calculateGrid();
        } else {
            legendItems = legendItems.map(function(d) { return parseFloat(d) || 0; }).sort(d3.ascending);
            if (activeLegendType.name !== "") {
                var range = d3.extent(legendItems);
                if (range[1]==range[0]){
                    range[0]=0.9*range[0];
                    range[1]=1.01*range[1]; // 1.1 gave a color not distinguishable enough, here it's red..
                }
                colorScale = d3.scaleSequential(interpolateRdYlBu).domain([range[1], range[0]]);
                colorsForScale = schemeRdYlBu[11];
            } else {
                colorsForScale = ["steelblue"];
                colorScale = d3.scaleOrdinal().range(colorsForScale);
            }
        }
    }

    function highlightColorBand(items)  {
        if (activeLegendType.name == "" || !activeLegendType.isNumber) {
            return;
        }
        var highlightBox = svg.select("#highlightvalue");
        var isHighlight = (items && items.length === 1);
        if (isHighlight) {
            var value = _.get(items[0], activeLegendType.name);
            var pos = colorBandScale(value);
            var format = (value < 1 ? d3.format(".2") : d3.format("d"));
            var textBox = highlightBox.select("text")
                .text(format(value));
            var bbox = textBox.node().getBBox();
            var boxWidth = bbox.width < 30 ? 30 : bbox.width;
            highlightBox.select("rect").attr("width", boxWidth);
            highlightBox.attr("transform", "translate(" + (sizeOfColorBand - (sizeOfColorBand / 5)) + "," + pos + ")");
        }
        highlightBox.style("opacity", isHighlight ? 1 : 0);
    }

    function drawLegendItems(legendItems, isHighlight) {
        var rectSize = isHighlight ? getLegendItemBoxSize() * 1.2 : getLegendItemBoxSize();
        var boxSize = isHighlight ? sizeOfColorLegendBox * 1.2 :sizeOfColorLegendBox ;
        legendItems.select("rect")
            .transition().duration(100)
            .attr("height", rectSize)
            .attr("width", rectSize)
            .style("fill", colorScale)
            .style("stroke", isHighlight ? "black" : "#ccc")
            .style("stroke-width", isHighlight ? "2px" : "1px");

        legendItems.select("text")
            .transition().duration(100)
            .attr("dx", boxSize)
            .attr("dy", boxSize / 2)
            .style("fill", colorScale)
            .attr("font-size", isHighlight ? 15 : 10 );
    }

    function highlightColorLegendItems(items) {
        if (activeLegendType.name === "" || activeLegendType.isNumber) {
            return;
        }
        var isHighlight = (items && items.length > 0);
        var legendItems = svg.selectAll("g.legenditem");
        drawLegendItems(legendItems, false);
        if (isHighlight) {
            //performance enhancement first make a set of the property and then check
            var propMap = d3.set(items.map(function(i) {
                return _.get(i, activeLegendType.name);
            }));
            legendItems = svg.selectAll("g.legenditem")
                .filter(function(d) {
                    return propMap.has(d);
            });
        }
        drawLegendItems(legendItems, isHighlight);
    }

    function highlightItems(items) {
        if (activeLegendType.isNumber) {
            highlightColorBand(items);
        } else {
            highlightColorLegendItems(items);
        }
    }
    function onColorLegendOver(e, d) {
        event.call("highlightlegend", this, e);
    }

    function onColorLegendOut(e, d) {
        event.call("unhighlightlegend", this, e);
    }

    function chart(selection) {

        draw = function() {
            var band = svg.selectAll("g.colorband")
                .data([activeLegendType], function(d) { return d.isNumber; });

            band.exit().attr("opacity", 0).remove();
            band = band.enter()
                .append("g")
                .attr("class", "colorband")
                .attr("transform", "translate(" + (activeLegendType.isNumber ? size[0] / 2 : margin) + "," + 15 + ")")
                .merge(band);
            band.style("display", function(d) { return d.name === "" ? "none" : "inline"; });

            if (!activeLegendType.isNumber) {
                var legendItems = band.selectAll("g.legenditem").data(colorScale.domain(), String);
                legendItems.exit()
                    .transition().duration(500)
                    .style("opacity", 0)
                    .remove();

                var newItems = legendItems.enter()
                    .append("svg:g")
                    .attr("class", "legenditem")
                    .style("opacity", 1e-6)
                    .attr("transform", positionLegendItem)
                    .on("mouseover", onColorLegendOver)
                    .on("mouseout", onColorLegendOut);
                    /*.on("click",chart.colorlegendclick);*/

                newItems.append("svg:rect")
                    .attr("height", getLegendItemBoxSize())
                    .attr("width", getLegendItemBoxSize())
                    .style("fill", colorScale)
                    .style("stroke", "#ccc");

                if (hasOneColumn()) {
                    newItems.append("svg:text")
                        .attr("dx", sizeOfColorLegendBox)
                        .attr("dy", sizeOfColorLegendBox / 2)
                        .attr("text-anchor", "start")
                        .attr("font-family", "Helvetica Neue, Helvetica, sans-serif")
                        .attr("font-size", "10px")
                        .style("fill", colorScale)
                        .text(function(d) { return d + " (" + legendMap.get(d).length + ")"; });
                }

                newItems.transition().duration(500)
                    .delay(500)
                    //.delay(function(d,i) { return 50 + i / legendSize * 100;})
                    .style("opacity", 1);
            } else {
                gradient.selectAll("*").remove();
                var pct = linspace(0, 100, colorsForScale.length).map(function(d) {
                    return Math.round(d) + "%";
                });
                var colourPct = d3.zip(pct, colorsForScale);
                colourPct.forEach(function(d) {
                    gradient.append("stop")
                        .attr("offset", d[0])
                        .attr("stop-color", d[1])
                        .attr("stop-opacity", 1);
                });
                var colorBand = band.selectAll("rect").data([activeLegendType.name], function(d) { return d.name; });
                var colorAxis = band.selectAll("g.axis").data([activeLegendType.name], function(d) { return d.name; });
                colorAxis = colorAxis
                    .enter()
                    .append("g")
                    .attr("class", "axis")
                    .attr("transform", "translate(" + sizeOfColorBand + ", 0)")
                    .merge(colorAxis);

                colorBand.enter()
                    .append("rect")
                        .attr("x1", 0)
                        .attr("y1", 0)
                    .merge(colorBand)
                    .attr("width", sizeOfColorBand)
                    .attr("height", getPlotHeight() )
                    .style("fill", "url(#gradient)");

                // create a scale and axis for the legend#
                var domain = colorScale.domain();
                colorBandScale = d3.scaleLinear()
                    .range([getPlotHeight(), 0])
                    .domain([domain[1], domain[0]]);

                var colorBandAxis = d3.axisRight(colorBandScale).ticks(6);
                colorAxis.call(colorBandAxis);

                var highlightBox = colorBand
                    .enter()
                        .append("svg:g")
                        .attr("id", "highlightvalue")
                        .attr("transform", "translate(" + (sizeOfColorBand - (sizeOfColorBand / 5)) + ",0)")
                        .style("opacity", 0);
                highlightBox.append("svg:rect")
                    .attr("x", 0)
                    .attr("y", 0)
                    .attr("height", "18px")
                    .attr("width", "30px")
                    .style("fill", "white")
                    .style("stroke", "#C2BFBF")
                    .style("shape-rendering", "crispEdges");
                highlightBox.append("svg:text")
                    .attr("x", 0)
                    .attr("y", 0)
                    .attr("transform", "translate(2,12)")
                    .style("fill", "black")
                    .style("font-size", "10px");
            }
        };

        selection.each(function(dt) {
            svg = d3.select(this);
            if (svg.selectAll("defs").empty()) {
                gradient = svg.append("svg:defs").append("svg:linearGradient")
                .attr("id", "gradient")
                .attr("x1", "0%")
                .attr("y1", "0%")
                .attr("x2", "0%")
                .attr("y2", "100%")
                .attr("spreadMethod", "pad");
            }
            data = dt;
            initLegend();
            draw();
        });
    }

    chart.size = function(value) {
        if (!arguments.length) {
            return size;
        }
        size = value;
        if (typeof draw === "function") {
            draw();
        }
        return chart;
    };

    chart.colorScale = function() {
        return colorScale;
    };

    chart.legendTypes = function() {
        return legendTypes;
    };

    chart.legendsToInclude = function(value) {
        if (!arguments.length) {
            return legendsToInclude;
        }
        legendsToInclude = value;
        return chart;
    };
    chart.activeLegendType = function(value) {
        if (!arguments.length) {
            return activeLegendType;
        }
        activeLegendType = value;
        if (typeof draw === "function") {
            initScales();
            draw();
        }
        return chart;
    };

    chart.highlightItems = function(value) {
       if (typeof highlightItems === "function") {
            highlightItems(value);
        }
    };
    chart.on = function() {
        var value = event.on.apply(event, arguments);
        return value === event ? chart : value;
    };

    return chart;
}
