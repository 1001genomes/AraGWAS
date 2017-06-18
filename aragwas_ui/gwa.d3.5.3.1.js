// hide context menu and SNP information if click on the outside of it
$(document).mouseup(function (e)
{
    var container = $('#newContMen');

    if (container.has(e.target).length === 0)
    {
        container.hide();
	$('#tooltip').hide();
	$('#zoomBar').remove();
    }
});

jQuery.fn.exists = function(){return this.length>0;}


// define function to move svg-element to the front
d3.selection.prototype.moveToFront = function() {
	return this.each(function(){
	this.parentNode.appendChild(this);
	});
};

/* User Agent (Browserkennung) auf einen bestimmten Browsertyp pr�fen */  
 function checkBrowserName(name){  
   var agent = navigator.userAgent.toLowerCase();  
   if (agent.indexOf(name.toLowerCase())>-1) {  
     return true;  
   }  
   return false;  
 }  


function plotZoomBar(svg,options,w,h,zero,snpBeg,snpEnd,full,paddingTop,scaleW,scaleH){
	if (!$('#zoomBarStat1'+options.div.replace("#","")).exists()){
		svg.append("rect")
			.attr("x",zero)
			.attr("y",paddingTop/1.5)
			.attr("id","zoomBarStat1"+options.div.replace("#",""))
			.attr("height", h/30)
			.attr("width", Math.round(snpBeg-zero))
			.style("fill", "rgb(200,200,200)");
                svg.append("rect")
	                .attr("x",Math.round(snpBeg))
	                .attr("y",paddingTop/1.5)
	                .attr("id","zoomBarStat2"+options.div.replace("#",""))
	                .attr("height",h/30)
	                .attr("width", Math.round(snpEnd-snpBeg))
	                .style("fill", "#08C");
                svg.append("rect")
	                .attr("x",Math.round(snpEnd))
        	        .attr("y",paddingTop/1.5)
			.attr("id","zoomBarStat3"+options.div.replace("#",""))
	                .attr("height",h/30)
        	        .attr("width", Math.round(full-snpEnd))
        	        .style("fill", "rgb(200,200,200)");
		svg.append("line")
			.attr("x1",zero)
			.attr("id","zoomLine1"+options.div.replace("#",""))
			.attr("y1",scaleH(options.max_y+1))
			.attr("x2",Math.round(snpBeg))
			.attr("y2",paddingTop/1.5+h/30)
            		.style("stroke", "#08C")
		        .style("stroke-width",1);
		svg.append("line")
			.attr("x1",full)
			.attr("id","zoomLine2"+options.div.replace("#",""))
			.attr("y1",scaleH(options.max_y+1))
			.attr("x2",Math.round(snpEnd))
			.attr("y2",paddingTop/1.5+h/30)
            		.style("stroke", "#08C")
		        .style("stroke-width",1);
	}
	else{
	$("#zoomBarStat1"+options.div.replace("#",""))
		.attr("width",Math.round(snpBeg-zero));
        $("#zoomBarStat2"+options.div.replace("#",""))
                .attr("x",Math.round(snpBeg))
                .attr("width",function(){
                                if ((snpEnd-snpBeg)< 5){
                                        return 5;
                                }
                                else{
                                        return Math.round(snpEnd-snpBeg);
                                }
                        });
        }
        $("#zoomBarStat3"+options.div.replace("#",""))
                .attr("x",function(){
	
				return (parseFloat($("#zoomBarStat2"+options.div.replace("#","")).attr('x'))+parseFloat($("#zoomBarStat2"+options.div.replace("#","")).attr('width')));
			})
                .attr("width", Math.round(full-snpEnd));
	$('#zoomLine1'+options.div.replace("#",""))
                .attr("x2",function(){
			return $("#zoomBarStat2"+options.div.replace("#","")).attr("x")
		});
        $('#zoomLine2'+options.div.replace("#",""))
                .attr("x2",function(){
                        return $("#zoomBarStat3"+options.div.replace("#","")).attr("x")
                });

}


// get informations
function plotManhattanD3(attr,bp_pos_global){

//Width and height
    var padding = 40;
    var paddingTop = 60; 
    var paddingBottom = 100; 
    var scaleW = d3.scale.linear();
    var scaleH = d3.scale.linear();
    var scaleWfixed = d3.scale.linear();
    var x = d3.scale.linear();
    var y = d3.scale.linear();
    var boxLevel = 0;
    var boxNum = -1;

    var options = {
	task_id:undefined,
        matrix: undefined,
        species_id: undefined,
        dataset_id: undefined,
        chr: 0,
        alpha: 0.05,
        max_y: 10,
        max_x: 10,
        bonferoniThreshold: 10,
        div: undefined,
        divLegend: undefined,
        xlabel: "x",
        ylabel: "y",
        legend1: "",
        legend2: "",
        color:0,
        limited:0,
        experiment_type:"GWAS"
    };
    //parse attr
    $.extend(options,attr);
    var w = d3.select(options.div).style('width').replace("px","");
    var h = d3.select(options.div).style('height').replace("px","");
    var divHeight = $(options.div).height();
// define scaling options
    scaleW.domain([0, options.max_x]);
    scaleW.range([padding, (w-padding)]);
    scaleH.domain([0, options.max_y+1]);
    scaleH.range([h-paddingBottom, paddingTop]);
    x.domain([padding, (w-padding)]);
    x.range([0, options.max_x]);
    scaleWfixed.domain([0, options.max_x]);
    scaleWfixed.range([padding, (w-padding)]);
    var full = scaleWfixed(options.max_x);
    var zero = scaleWfixed(0);

// ajax request to get tooltip-information for a single SNP
function tooltipdata(d){
	var x = d[0];
	var y = d[1];
	var gene = "";
	if (options.genome_annotation_id!=-1) {
		var scriptUrl = "/gwas/results/manhattan/annotate/" + options.species_id + "/" + options.genome_annotation_id + "/" + options.chr + "/" + x + "/";
        $.ajax({
            url: scriptUrl,
            type: 'get',
            dataType: 'html',
            async: false,
            success: function(data) {
                    gene = data;
            }
        });
		if(gene!="") {
			gene = "Gene: "+gene;
		}
	} 
    
	y = Math.round((y*100))/100;
	var mouseCoords = d3.mouse(svg[0][0].parentElement);
	$('#t1').text("SNP-Pos: " + x);
	$('#t2').text(options.ylabel + ": " + y);
    $('#t3').text(gene);
    if(options.experiment_type=="GWAS"){
        $('#t4').text("Click for more information!")
        $('#t4').css({"color":"#66B266","font-weight":"900"})
    }
	//$('#tooltip').css({"top": (d3.event.pageY-10)+"px", "left":(d3.event.pageX+10)+"px","position":"absolute","background-color":"white","padding":"2px","z-index":"10","border":"1px solid #ccc"});
    $('#tooltip').css({"top": (d3.event.pageY-mouseCoords[1]-15)+"px", "left":(mouseCoords[0]+30)+"px",
	    "position":"absolute","background-color":"black","color":"white",
		"opacity": "0.7",
	    "filter": "alpha(opacity=70)",
		"padding":"2px","z-index":"100","border":"1px solid transparent",
		"border-radius": "4px"});
     /*$('#tooltip').css({"top": ($(this).offset().top-div_tip_height-10)+"px", "left":(mouseCoords[0]+10)+"px",
				        	"position":"absolute","background-color":"black","color":"white",
							"opacity": "0.7",
						    "filter": "alpha(opacity=70)",
							"padding":"2px","z-index":"100","border":"1px solid transparent",
							"border-radius": "4px"});*/

        $('#tooltip').show();
//	return //text
};


// define colors
    var blue = 204 - (options.color) * 40;
    var red = 51 + (options.color) * 40;
// get data
    var data = options.matrix;
    var d2 = [[0,options.bonferoniThreshold],[options.max_x,options.bonferoniThreshold]];
// draw svg
    var svg = d3.select(options.div)
            .append("svg")
            .attr("width", w)
            .attr("height", h-paddingBottom+padding);
	var len = Math.pow(10,((String(Math.round(options.max_x/5)).length-1)));	
	var val_x = Math.round(options.max_x/5/len)*len;
	var aktuell = false;


// remover highlited circles, for IE workaround
		svg.on("mouseenter",function(d){
		if(aktuell){
                $('#tooltip').hide();
                aktuell.style("fill", function(d){
        	        if (!(d[0] == eval(bp_pos_global))){
        		        return ("rgba("+red+",102,"+blue+",1)");
        	        }   
               		else{  
                		return ("rgba("+(255-red)+","+(255-102)+","+(255-blue)+",1)");
                	}
                })
		.attr("r", 2.1).style("stroke","");
                aktuell = false;
                }
        })



// draw graph help-lines in background
for (var i = 0; (val_x*i) < options.max_x ; i++) {
     svg.append("svg:line").attr("class","helpLine")
            .attr("x1", scaleW(val_x*i))
            .attr("y1", scaleH(0))
            .attr("x2", scaleW(val_x*i))
            .attr("y2", scaleH(options.max_y+1))
            .style("stroke", "#CCC")
            .style("stroke-width",1);
    svg.append("svg:g").attr("class","posText")
            .attr("transform", "translate("+scaleW(val_x*i)+","+(h-paddingBottom/1.2)+")")
            .append("text").text(val_x*i)
            .attr("text-anchor", "middle");
};
	var val_y = Math.round(options.max_y/3)
for (var i = 1; (i*val_y) < (options.max_y+1); i++) {
     svg.append("svg:line")
            .attr("x1", scaleW(0))
            .attr("y1", scaleH(val_y*i)) 
            .attr("x2", scaleW(options.max_x))
            .attr("y2", scaleH(val_y*i))          
            .style("stroke", "#CCC")
            .style("stroke-width",1);
    svg.append("svg:g")
            .attr("transform", "translate("+(padding/1.5)+","+scaleH(val_y*i)+")")
            .append("text").text(val_y*i)
            .attr("text-anchor", "middle");
};
// write text-information to axis and draw graph-elements
    svg.append("svg:g")
	    .attr("transform", "translate("+5+","+12+")")
	    .append("text").text("Manhattan-plot for chromosome "+ options.chr)
	    .style("font-weight","bold")
    svg.append("svg:g")
            .attr("transform", "matrix(0, -1, 1, 0, 0, 0)").append("svg:g")
	    .attr("transform", "translate("+((paddingBottom-h))+","+(padding/3)+")")
	    .append("text").text(options.ylabel);
    svg.append("svg:g")
            .attr("transform", "translate("+((w-padding)/2)+","+(h-paddingBottom/1.5)+")")
            .append("text").text("chromosomal position [bp]")
            .attr("text-anchor", "middle");
    svg.append("rect")
	    .attr("x", padding)
	    .attr("y", padding/2)
	    .attr("width", padding/2.5)
	    .attr("height", padding/3.5)
            .style("fill", "rgba("+red+",102,"+blue+",1)");
    svg.append("svg:g")
            .attr("transform", "translate("+(padding+25)+","+(padding/1.3)+")")
            .append("text").text(options.legend1);
    svg.append("rect")
            .attr("x", padding*5.5)
            .attr("y", padding/2)
            .attr("width", padding/2.5)
            .attr("height", padding/3.5)
            .style("fill", "rgb(0,100,0)");
     svg.append("svg:line")
            .attr("x1", scaleW(0))
            .attr("y1", scaleH(options.max_y+1))
            .attr("x2", scaleW(options.max_x))
            .attr("y2", scaleH(options.max_y+1))
            .style("stroke", "#CCC")
            .style("stroke-width",1.5 );
     svg.append("svg:line")
            .attr("x1", scaleW(options.max_x))
            .attr("y1", scaleH(0))
            .attr("x2", scaleW(options.max_x))
            .attr("y2", scaleH(options.max_y+1))
            .style("stroke", "#CCC")
            .style("stroke-width",1.5 );
     svg.append("svg:line")
            .attr("x1", scaleW(0))
            .attr("y1", scaleH(0))
            .attr("x2", scaleW(0))
            .attr("y2", scaleH(options.max_y+1))
            .style("stroke", "#000000")
            .style("stroke-width",1);
     svg.append("svg:line")
            .attr("x1", scaleW(0))
            .attr("y1", scaleH(0))
            .attr("x2", scaleW(options.max_x))
            .attr("y2", scaleH(0))
            .style("stroke", "#000000")
            .style("stroke-width",1);
     svg.append("svg:g")
            .attr("transform", "translate("+(padding*5.5+25)+","+(padding/1.3)+")")
            .append("text").text(options.legend2);
     svg.append("svg:line")
            .attr("x1", scaleW(d2[0][0]))
            .attr("y1", scaleH(d2[0][1]))
            .attr("x2", scaleW(d2[1][0]))
            .attr("y2", scaleH(d2[1][1]))
            .style("stroke", "rgb(0,100,0)")
            .style("stroke-width",1.5 );


// draw datapoints

if(checkBrowserName('MSIE')){  

var aktuell = false;
     svg.selectAll("circle")
     	.data(data)
        .enter()
        .append("circle")
        .attr("cx", function(d) {
                return scaleW(d[0]);
         })
        .attr("cy", function(d) {
                return scaleH(d[1]);
         })
        .attr("r", 2.1)
        .style("fill", function(d){
               	if (!(d[0] == eval(bp_pos_global))){
                	return ("rgba("+red+",102,"+blue+",1)");
                }   
                else{  
                	return ("rgba("+(255-red)+","+(255-102)+","+(255-blue)+",1)");
                }
                })

	.on("mouseenter",function(d){
		if (!aktuell){
		d3.select(this).style("stroke", "rgba("+(255-red)+","+(255-102)+","+(255-blue)+",0.65)").style("stroke-width",10 );
		d3.select(this).style("fill", "rgba("+(255-red)+","+(255-102)+","+(255-blue)+",1)").moveToFront();
                d3.select(this).attr("z-index","1000");
		tooltipdata(d);
		aktuell = d3.select(this);
		}
	});


}

else {
     svg.selectAll("circle")
        .data(data)
        .enter()
        .append("circle")
        .attr("cx", function(d) {
                return scaleW(d[0]);
         })
        .attr("cy", function(d) {
                return scaleH(d[1]);
         })
        .attr("r", 2.1)
        .style("fill", function(d){
		if (!(d[0] == eval(bp_pos_global))){
			return ("rgba("+red+",102,"+blue+",0.65)");
		}
		else{
            return ("rgba("+(255-red)+","+(255-102)+","+(255-blue)+",0.65)");
		}
		})
        .on("mouseover",function(d){
 

                d3.select(this).style("stroke", "rgba("+(255-red)+","+(255-102)+","+(255-blue)+",0.65)").style("stroke-width",10 );
                d3.select(this).style("fill", "rgba("+(255-red)+","+(255-102)+","+(255-blue)+",0.65)").moveToFront();
                d3.select(this).attr("z-index","1000");
                tooltipdata(d);
        })

        .on("mouseout", function(){
                        $('#tooltip').hide();
                        d3.select(this).style("fill", function(d){
                if (!(d[0] == eval(bp_pos_global))){
                return ("rgba("+red+",102,"+blue+",0.65)");
                }   
                else{  
                return ("rgba("+(255-red)+","+(255-102)+","+(255-blue)+",0.65)");
                }
                })

				.attr("r", 2.1).style("stroke","");
        });

}


//////////////////////////////////////////////// detailed SNP-View on click ======================================================================>>>>>

if(options.experiment_type=="GWAS") {
    svg.selectAll("circle").data(data).on("click", function(d){
        window.location.href = '/gwas/results/snp/detailed/'+options.task_id+'/'+options.chr+'/'+d[0]+'/';
    });
}

//<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< end detailed SNP-View on db-click ============================================================/////////////////////////

var xBeg,yBeg,xNow,yNow,xEnd,yEnd;
var isWebkit = (window.URL != null);

if(!bp_pos_global){
svg.on("mousedown",function(){
   		if(isWebkit){
			var mouseCoords = d3.mouse(svg[0][0].parentElement);
			xBeg = mouseCoords[0];
		} else {
			xBeg = d3.event.pageX;
		}
	     svg.append("rect")
		.attr("id","zoomBar")
		.attr("x", xBeg-0.02)
            	.attr("y", scaleH(options.max_y+1))
            	.attr("width", 0)
            	.attr("height", scaleH(0)-scaleH(options.max_y+1))
            	.style("fill", "rgba(184,184,184,0.5)");
		d3.event.preventDefault();

		svg.on("mousemove",function(){
			if(isWebkit) {
				var mouseCoords = d3.mouse(svg[0][0].parentElement);
				xNow = mouseCoords[0];
			} else {
				xNow= d3.event.pageX;
			}
			if (xNow > xBeg){
				$('#zoomBar').attr("width",(xNow-xBeg));
			}
			if (xNow < xBeg){
				$('#zoomBar').attr("x", (xNow)).attr("width",Math.abs(xBeg-xNow));
				d3.event.preventDefault();
			}
		});
	    svg.on("mouseup",function(d){
			xWidth = $(this).width();
			if(isWebkit) {
				var mouseCoords = d3.mouse(svg[0][0].parentElement);
				xEnd = mouseCoords[0];
			} else {
				xEnd = d3.event.pageX;
			}
			$('#zoomBar').remove();
			zoom();
		});
});



svg.on("contextmenu",function(){
	$(options.div).height(255);
	$(this).remove();
	plotManhattanD3(attr);
	$('#zoomBarStat1').remove();
	$('#zoomBarStat2').remove();
	$('#zoomBarStat3').remove();
	$('.geneBox').remove();
	$('#TtooltipGene').hide();
	boxLevel = 0;
	boxNum = -1;
        d3.event.preventDefault();
return false;
});

}
else{
svg.on("contextmenu",function(){
        $(options.div).height(255);
        $(this).remove();
        d3.event.preventDefault();
        $('#zoomBarStat1').remove();
        $('#zoomBarStat2').remove();
        $('#zoomBarStat3').remove();
        $('.geneBox').remove();
        $('#TtooltipGene').hide();
        boxLevel = 0;
        boxNum = -1;
        plotManhattanD3(attr,bp_pos_global);
	return false;
  });
}

        $('#loader').remove();



function zoom(){
	var beg = Math.round(x(xBeg));
	var end = Math.round(x(xEnd));
	var tmp;
	if (beg > end){
		tmp = beg;
		beg = end;
		end = tmp;
	}
 
	var snpBeg = scaleWfixed(beg);
	var snpEnd = scaleWfixed(end);
  
	if ((end-beg) <= 2){
		return false
	}
	x.range([beg, end]);

	scaleW.domain([beg,end]);

	

/////////////////////////////////////////////////////////////// geneView ===============================================================>>

// only calculate and draw genes, if checkbox is checked
if ($("#showGenes").attr('checked') || (bp_pos_global)){
  var beg_pos = beg-10000;
  if(beg_pos<0) beg_pos=0;
  var annos =  $.getJSON("/gwas/results/manhattan/annotate/plot/"+options.species_id+"/"+options.genome_annotation_id+"/"+options.chr+"/"+beg_pos+"/"+(end+10000)+"/",function(data){
//	if (data.anno.length >=100) {return }  //IMPORTANT!!! sets max. number of genes displayed 



  var tooltipGene = new Array();
  var geneLevelClosed = new Array();
  var geneLevel = 0;
  var yGene = new Array();

  geneLevelClosed[0] = scaleW(data.anno[0][2]);
  yGene[0] = 0;

//calculate level where gene is displayed

	for(i=1; i < (data.anno.length) ; i++){
		for(l=0; l <= geneLevel ; l++){
			if((geneLevelClosed[l]) <= scaleW(data.anno[i][1])){
				yGene[i] = l;
				if (Math.abs(scaleW(data.anno[i][1])-scaleW(data.anno[i][1])) < 10){
					geneLevelClosed[l] = scaleW(data.anno[i][2])+10;
				}
				else{
					geneLevelClosed[l] = scaleW(data.anno[i][2]);
				}
				break;
			}
			else if(l == geneLevel){
				geneLevel += 1;
				geneLevelClosed[geneLevel] = scaleW(0);
			}
		}
	}

// display genes
        for(i=0; i < data.anno.length ; i++){
		tooltipGene[data.anno[i][0]] = new Array(data.anno[i][1], data.anno[i][2], data.anno[i][3])
		drawArrow(data,i,tooltipGene,yGene,beg,end);
	}

//resize div/svg to updated size, influenced by genes

	$(options.div).height(divHeight+geneLevel*10);
	svg.attr('height',$(options.div).height());


  });

}

//========================================================================>> geneView /////////////////////////////////////////////////////////

else {

// if no genes displayed, restore original div/svg size

	$(options.div).height(divHeight);
        svg.attr('height',$(options.div).height());

}

  var t = svg.transition()
      .duration(750);

  t.selectAll("circle")
      .attr("cx", function(d) { 
		if((d[0] > beg) && (d[0] < end)){
			return scaleW(d[0]); 
		}
		else {
			 $(this).remove(); 
		}
	});




	svg.selectAll(".helpLine").remove();
	svg.selectAll(".posText").remove();
	svg.selectAll(".gene").remove();
	svg.selectAll(".geneAnno").remove();
	svg.selectAll(".geneBox").remove();
	boxLevel = 0;
	boxNum = -1;

        var len = Math.pow(10,((String(Math.round((end-beg)/5)).length-1)));
	if (len == 0){
		len =1;
	}
        var val_x = Math.round((end-beg)/5/len)*len;
// draw graph help-lines in background

for (var i = 0; (val_x*i) < options.max_x ; i++) {
    if (((val_x*i) >= beg) && ((val_x*i) <= end)){
     svg.append("svg:line").attr("class","helpLine")
            .attr("x1", scaleW(val_x*i))
            .attr("y1", scaleH(0))
            .attr("x2", scaleW(val_x*i))
            .attr("y2", scaleH(options.max_y+1))
            .style("stroke", "#CCC")
            .style("stroke-width",1);
    svg.append("svg:g").attr("class","posText")
            .attr("transform", "translate("+scaleW(val_x*i)+","+(h-paddingBottom/1.2)+")")
            .append("text").text(val_x*i)
            .attr("text-anchor", "middle");
		}
	};

	plotZoomBar(svg,options,w,h,zero,snpBeg,snpEnd,full,paddingTop,scaleW,scaleH);

if (!bp_pos_global){
  d3.event.stopPropagation();
}
}


///////////////////////////////////////////////////////draw Arrow ===========================================================>


// uncomment for production
var lineData;
//var startArrow;
//var endArrow;
var hArr = 4;
//var yArr;
//var orientationArr;
//var tooltipGene;

function drawArrow(data,i,tooltipGene,yGene,beg,end){
	if ((data.anno[i][2] < beg) | (data.anno[i][1] > end)) return;

// remove for production
var	ArrName = data.anno[i][0];
var	ArrStart = data.anno[i][1];
var	ArrEnd = data.anno[i][2];

// remove "var" for production
var	startArrow = scaleW(data.anno[i][1]);
var	endArrow = scaleW(data.anno[i][2]);
var	orientationArr = data.anno[i][3];
var	tooltipGene = tooltipGene
var	yArr =  (h-paddingBottom+yGene[i]*(10)+40);
var	lenArr = Math.abs(startArrow - endArrow);

	if (lenArr < 10) lenArr = 10;
	
	lineData = function(){
// special case, arrow begins too left, shorten arrow & print red mark
		if (parseInt(data.anno[i][1]) < beg){
			startArrow = scaleW(beg);
			lenArr = Math.abs(startArrow - endArrow);
 			svg.append("svg:rect")
				.attr("class","geneAnno")
        	                .attr("x",(startArrow))
                	        .attr("y",(yArr-0.5*hArr))
                        	.attr("width",1)
          			.attr("height",(2*hArr))
	                        .attr("fill","red")
	                        .attr("stroke","red")
	                        .attr("stroke-width",2);
		}
// special case, arrow ends too right, shorten arrow & print red mark
		if (parseInt(data.anno[i][2]) > end){
			endArrow = scaleW(end);
			lenArr = Math.abs(startArrow - endArrow);
	                svg.append("svg:rect")
				.attr("class","geneAnno")
                	        .attr("x",(endArrow-1))
                        	.attr("y",(yArr-0.5*hArr))
	                        .attr("width",1)
        	                .attr("height",(2*hArr))
                	        .attr("fill","red")
                        	.attr("stroke","red")
	                        .attr("stroke-width",2);
		}

// coordinates for arrow
		if(orientationArr == "+"){
		// path for arrow to right side
                      var l = [{"x": (startArrow),			"y": (yArr) },
                               {"x": (startArrow+lenArr-(1.5*hArr)),    "y": (yArr)},
                               {"x": (startArrow+lenArr-(1.5*hArr)),    "y": (yArr-(0.5*hArr))},
                               {"x": (startArrow+lenArr),             	"y": (yArr+(0.5*hArr))},
                               {"x": (startArrow+lenArr-(1.5*hArr)),    "y": (yArr+(1.5*hArr))},
                               {"x": (startArrow+lenArr-(1.5*hArr)),    "y": (yArr+hArr)},
                               {"x": (startArrow),                    	"y": (yArr+hArr)},
                               {"x": (startArrow),                    	"y": (yArr)}]
		}
		else {
		// path for arrow to left side
                      var l = [
                                {"x": (startArrow),            		"y": (yArr+(0.5*hArr))},
                                {"x": (startArrow+(1.5*hArr)), 		"y": (yArr-(0.5*hArr))},
                                {"x": (startArrow+(1.5*hArr)),		"y": (yArr)},
				{"x": (startArrow+lenArr), 		"y": (yArr) },
                                {"x": (startArrow+lenArr),              "y": (yArr+hArr)},
                                {"x": (startArrow+(1.5*hArr)), 		"y": (yArr+hArr)},
                                {"x": (startArrow+(1.5*hArr)),     	"y": (yArr+(1.5*hArr))},
                                {"x": (startArrow),            		"y": (yArr+(0.5*hArr))},
			       ]
		}

		return l;	
	};

// returns arrows as path
	var lineFunction = d3.svg.line()
		.x(function(d) { return d.x; })
		.y(function(d) { return d.y; });
	
// draw arrow, use path constructed from coordinates
	var lineGraph = svg.append("path")
		.attr("d", lineFunction(lineData()))
		.attr("stroke", "#7C7C7C")
		.attr("class","geneAnno")
		.attr("stroke-width", 1)
		.attr("fill", function(){
			if (orientationArr == "+") return "#AEC6CF";//"#62D6F6";
			return "#FFB347"})//"#D7F63C"})
		.attr("id",data.anno[i][0])
// show tooltip on hover
	        .on("mouseover", function(){
			var mouseCoords = d3.mouse(svg[0][0].parentElement);
			 var div_tip_height = parseFloat($('#Ttooltip').height());
        	        $('#tt1').text("Name: "+this.id);
                        $('#tt2').text("Start Position: "+tooltipGene[this.id][0]);
                        $('#tt3').text("End Position: "+tooltipGene[this.id][1]);
                        $('#tt4').text("Strand: "+tooltipGene[this.id][2]);
                        //$('#Ttooltip').css({"top": (d3.event.pageY-10)+"px", "left":(d3.event.pageX+10)+"px","position":"absolute","background-color":"white","padding":"2px","z-index":"10","border":"1px solid #ccc"});
                        $('#Ttooltip').css({"top": ($(this).offset().top-div_tip_height-60)+"px", "left":(mouseCoords[0]+30)+"px",
								        	"position":"absolute","background-color":"black","color":"white",
											"opacity": "0.7",
										    "filter": "alpha(opacity=70)",
											"padding":"2px","z-index":"100","border":"1px solid transparent",
											"border-radius": "4px"});
                	$('#Ttooltip').show();


                })
// hide tooltip
	        .on("mouseout", function(){
                	$('#Ttooltip').hide();
        	})
// show fixed tooltip on click
		/*.on("click", function(d) {
			var mouseCoords = d3.mouse(svg[0][0].parentElement);
			$('#ttt1').text("Name: "+this.id);
                        $('#ttt2').text("Start Position: "+tooltipGene[this.id][0]);
                        $('#ttt3').text("End Position: "+tooltipGene[this.id][1]);
                        $('#ttt4').text("Strand: "+tooltipGene[this.id][2]);
                        //$('#TtooltipGene').css({"top": (d3.event.pageY+3)+"px", "left":(d3.event.pageX+3)+"px","position":"absolute","background-color":"white","padding":"2px","z-index":"5","border":"1px solid #ccc"});
                        $('#TtooltipGene').css({"top": (d3.event.pageY-mouseCoords[1]-3)+"px", "left":(mouseCoords[0]+3)+"px",
									        	"position":"absolute","background-color":"black","color":"white",
												"opacity": "0.7",
											    "filter": "alpha(opacity=70)",
												"padding":"2px","z-index":"100","border":"1px solid transparent",
												"border-radius": "4px"});
                
                        $('#TtooltipGene').show()})
                        */
// draw gene-information on doublecklick
		.on("dblclick", function(d) {
			drawGeneInfo(Math.max.apply(null,yGene),yGene[i],yArr,hArr,data.anno[i][0],data.anno[i][1],data.anno[i][2],data.anno[i][3],beg,end,startArrow);
			d3.event.preventDefault();
		});





}

// hide fixed gene-tooltip
/*
  $('#TtooltipGene').on("click", function() { 
	$('#TtooltipGene').hide();
  });
*/
//====================================================>draw Arrow \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\







///////////////////////////////////////////////////////draw custom gene info ===========================================================>

function drawGeneInfo(yMax,yGene,yArr,hArr,geneName,geneBeg,geneEnd,geneOrientation,beg,end,startArrow){
	
var	boxSpaceBeg = scaleW(beg);	
var	boxSpaceEnd = scaleW(end);	
var	boxHeight = 70;
var	boxWidth = 170;
var 	textSizeGene = 3;
var	yPaddingText = 15;
var	xPaddingText = 4;
var	paddingText = 15;


var	boxSpaceUsed = (scaleW(beg)+(boxWidth*boxNum));	
var	yBox =  (h-paddingBottom+(yMax*10)+50+boxLevel*boxHeight);


	if((boxSpaceUsed+2*boxWidth) > boxSpaceEnd){
		boxLevel += 1;
		boxNum = 0;
	}
	else{
		boxNum += 1;
	}	


	boxSpaceUsed = (scaleW(beg)+(boxWidth*boxNum));	
	yBox =  (h-paddingBottom+(yMax*10)+50+boxLevel*boxHeight);

	$(options.div).height(divHeight+yMax*10+boxHeight*boxLevel+20);
	svg.attr('height',$(options.div).height());
	
	svg.append("svg:rect")
		.attr("x",boxSpaceUsed)
		.attr("y",yBox)
		.attr("width",boxWidth-4)
		.attr("height",boxHeight-4)
		.attr("stroke","black")
		.attr("stroke-width",1)
		.attr("fill","white")
		.attr("class","geneBox")
		.attr("id",geneName+"box");

	svg.append("svg:g")
		.attr("transform", "translate("+(boxSpaceUsed+xPaddingText)+","+(yBox+yPaddingText)+")")
		.append("text").text("Name: "+geneName)
		.attr("class","geneBox")
		.attr("size",textSizeGene);
	svg.append("svg:g")
		.attr("transform", "translate("+(boxSpaceUsed+xPaddingText)+","+(yBox+yPaddingText+paddingText)+")")
		.append("text").text("Start Position: "+geneBeg)
		.attr("class","geneBox")
		.attr("size",textSizeGene);
	svg.append("svg:g")
		.attr("transform", "translate("+(boxSpaceUsed+xPaddingText)+","+(yBox+yPaddingText+(+paddingText*2))+")")
		.append("text").text("End Position: "+geneEnd)
		.attr("class","geneBox")
		.attr("size",textSizeGene);
	svg.append("svg:g")
		.attr("transform", "translate("+(boxSpaceUsed+xPaddingText)+","+(yBox+yPaddingText+(paddingText*3))+")")
		.append("text").text("Strand: "+geneOrientation)
		.attr("class","geneBox")
		.attr("size",textSizeGene);

	lineDataBox = function(){
        	var l = [
                {"x": (boxSpaceUsed),   	       		"y": (yBox)},
                {"x": (startArrow+2),	 	          	"y": (yArr+0.5*hArr)},]
		return l;
	}

        var lineFunctionBox = d3.svg.line()
                .x(function(d) { return d.x; })
                .y(function(d) { return d.y; });


        var lineGraph = svg.append("path")
                .attr("d", lineFunctionBox(lineDataBox()))
                .attr("stroke", "black")
                .attr("class","geneBox")
		.style("stroke-opacity", 0.6)
                .attr("stroke-width", 1);


	$('#TtooltipGene').hide();

}

//====================================================>draw custom gene info \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
 
  if(bp_pos_global){
    zoom(bp_pos_global);
  }

}


function plotHistogram(attr){
    var options = {
        matrix: undefined,
        max_y: 15,
        max_x: 7,
        min_x: 0,
        div: undefined,
        divLegend: undefined,
        xlabel: "x",
        ylabel: "y",
        legend1: "",
        legend2: "",
        barWidth:0.3,
        toolbox_label:"Phenotype range",
        lastBin:0.0,
        ranges:undefined
    };
    var privateBarColor = "#f0ad4e";
	var private_hover = "#9E5B00";
	var private_stroke = "#C78425"
	var publicBarColor = "#4cae4c";
	var public_hover = "#238523";
	var public_stroke = "#005C00"
		
    //parse attr
    $.extend(options,attr);
    var data = options.matrix;
    var padding = 35;
    var w = d3.select(options.div).style('width').replace("px",""); 
    var h = d3.select(options.div).style('height').replace("px","");
    var scaleW = d3.scale.linear();
    var scaleH = d3.scale.linear();

    if (options.color==1) {
    	barColor = privateBarColor;
    	hover = private_hover;
    	stroke = private_stroke;
    } else {
    	barColor = publicBarColor;
    	hover = public_hover;
    	stroke = public_stroke;
    }
    
    //var blue = 204 - (options.color) * 40;
    //var red = 51 + (options.color) * 40;
    //var barColor = "rgb(" + red + ",102," + blue + ")";

// define scaling options
    scaleW.domain([options.min_x, options.max_x]);
    scaleW.range([padding, w-padding]);
    scaleH.domain([0, options.max_y+1]);
    scaleH.range([h-padding, padding]);

    var svg = d3.select(options.div)
            .append("svg")
            .attr("width", w)
            .attr("height", h);

    var aktuell = false;

/*
 // remover highlited circles, for IE workaround
 svg.on("mouseenter",function(d){
                 if(aktuell){
                 $('#tooltip').hide();
//                 d3.select(".bars").attr("fill", barColor);
 svg.selectAll(".bars").attr("fill", barColor);
                 aktuell = false;
                 }
         })
*/



// draw graph-helplines
	var num_lines = 8;
	if ((options.max_x - options.min_x) < 8 && (options.max_x - options.min_x) > 4 ){
		var val_x = 1;
	}
	else{
		var val_x = parseFloat(((options.max_x - options.min_x)/8).toPrecision(1));
	}
	if (val_x > 1){
		par_len = 0;
	}
	else{
        var per_len = String(parseFloat(val_x.toPrecision(1))).replace(".","").length-1;
	}
for (var i = 1; (i*val_x) < (options.max_x)  ; i++) {
    if ((i*val_x) > options.min_x){
     svg.append("svg:line")
            .attr("x1", scaleW(val_x*i))
            .attr("y1", scaleH(0))
            .attr("x2", scaleW(val_x*i))
            .attr("y2", scaleH(options.max_y+1))
            .style("stroke", "#CCC")
            .style("stroke-width",1);
    svg.append("svg:g")
            .attr("transform", "translate("+scaleW(val_x*i)+","+(h-padding/1.5)+")")
            .append("text").text((val_x*i).toFixed(per_len))
            .attr("text-anchor", "middle");
	}
};

for (var i = 0; (i*val_x) > options.min_x  ; i--) {
     svg.append("svg:line")
            .attr("x1", scaleW(val_x*i))
            .attr("y1", scaleH(0))
            .attr("x2", scaleW(val_x*i))
            .attr("y2", scaleH(options.max_y+1))
            .style("stroke", "#CCC")
            .style("stroke-width",1);
    svg.append("svg:g")
            .attr("transform", "translate("+scaleW(val_x*i)+","+(h-padding/1.5)+")")
            .append("text").text((val_x*i).toFixed(per_len))
            .attr("text-anchor", "middle");
};

        var val_y = Math.round(options.max_y.toPrecision(1)/5)
for (var i = 0; (i*val_y) < (options.max_y+1); i++) {
     svg.append("svg:line")
            .attr("x1", scaleW(options.min_x))
            .attr("y1", scaleH(val_y*i))
            .attr("x2", scaleW(options.max_x)+1)
            .attr("y2", scaleH(val_y*i))
            .style("stroke", "#CCC")
            .style("stroke-width",1);
    svg.append("svg:g")
            .attr("transform", "translate("+(padding/1.5)+","+scaleH(val_y*i)+")")
            .append("text").text(val_y*i)
            .attr("text-anchor", "middle");
};
// draw axis-text
    svg.append("svg:g")
            .attr("transform", "matrix(0, -1, 1, 0, 0, 0)").append("svg:g")
            .attr("transform", "translate("+(padding-h/1.4)+","+(padding/3.5)+")")
            .append("text").text("Frequency");
// draw x- and y-axis
     svg.append("svg:line")
            .attr("x1", scaleW(options.min_x))
            .attr("y1", scaleH(0))
            .attr("x2", scaleW(options.min_x))
            .attr("y2", scaleH(options.max_y+1))
            .style("stroke", "#ccc")
            .style("stroke-width",1);
     svg.append("svg:line")
            .attr("x1", scaleW(options.min_x))
            .attr("y1", scaleH(0))
            .attr("x2", scaleW(options.max_x)+1)
            .attr("y2", scaleH(0))
            .style("stroke", "#ccc")
            .style("stroke-width",1);
     svg.append("svg:line")
            .attr("x1", scaleW(options.min_x))
            .attr("y1", scaleH(options.max_y+1))
            .attr("x2", scaleW(options.max_x)+1)
            .attr("y2", scaleH(options.max_y+1))
            .style("stroke", "#CCC")
            .style("stroke-width",1.5 );
     svg.append("svg:line")
            .attr("x1", scaleW(options.max_x)+1)
            .attr("y1", scaleH(0))
            .attr("x2", scaleW(options.max_x)+1)
            .attr("y2", scaleH(options.max_y+1))
            .style("stroke", "#CCC")
            .style("stroke-width",1.5 );
// draw graph-elements
     svg.selectAll("rect")
            .data(data)
	    .enter()
	    .append("rect")
	    .attr("x", function(d){
			return (scaleW(d[0])+.5);
		})
	    .attr("y", function(d){
			return (scaleH(d[1]));
		})
	    .attr("width",function(d){
			if ((scaleW(d[0]+options.barWidth)) >= scaleW(options.max_x)+1 ){
				return Math.abs((scaleW(options.max_x)+1-scaleW(d[0]))-1);
			}
			else {
				return Math.abs(scaleW(d[0]+options.barWidth)-scaleW(d[0])-1);
			}
})
	    .attr("height", function(d){
			return (scaleH(0.1)-scaleH(d[1]))
})
            .attr("fill", barColor)
	    .attr("class", "bars")
	    .attr("stroke",stroke).attr("stroke-width","1px")
	    .attr("id", function(d){
                        return d[0];
})



            .on("mouseover",function(d,i){
				svg.selectAll(".bars").attr("fill", barColor);
				aktuell = d3.select(this);
		        d3.select(this).attr("fill", hover).moveToFront(); //
				var x = parseFloat(d3.select(this).attr("x").replace("px",""));
				var y = parseFloat(d3.select(this).attr("y").replace("px",""));
				var xp = $(this).parent().parent().parent().parent();
		        var div_tip_height = parseFloat($('#tooltip').height());
		        var mouseCoords = d3.mouse(svg[0][0].parentElement);
			    var range = options.ranges[i];
		       	var frequency = d[1];
		        $('#t1').text(options.toolbox_label + ": " + range);
			    $('#t2').text("Frequency: " + frequency);
		        $('#tooltip').css({"top": (d3.event.pageY-mouseCoords[1])+"px", "left":(mouseCoords[0])+"px",
		        							"position":"absolute","background-color":"black","color":"white",
		        							"opacity": "0.7",
					            		    "filter": "alpha(opacity=70)",
		        							"padding":"2px","z-index":"100","border":"1px solid transparent",
		        							"border-radius": "4px"});
                try{
            		$('#tooltip').css({"top": $(this).offset().top-div_tip_height-100, "left":mouseCoords[0]+10,
            							"position":"absolute",
				            			"background-color":"black","color":"white",
				            			"opacity": "0.7",
				            		    "filter": "alpha(opacity=70)",
										"padding":"2px","z-index":"100","border":"1px solid transparent",
										"border-radius": "4px"});
            		}
            		catch(err){
                            $('#tooltip').css({"top": $(this).offset().top-$(xp).offset().top-div_tip_height-15, "left":mouseCoords[0]-$(xp).offset().left+10,
												"position":"absolute",
												"opacity": "0.7",
						            		    "filter": "alpha(opacity=70)",
						            			"background-color":"black","color":"white",
												"padding":"2px","z-index":"100","border":"1px solid transparent",
												"border-radius": "4px"});
            		}
        	        $('#tooltip').show();
                    })
                    .on("mouseout", function(){
                                $('#tooltip').hide();
                                d3.select(this).attr("fill", barColor);
                    });                
					
$('#loader').remove();       
}


function plotHistogramPreview(attr){
    var options = {
        matrix: undefined,
        max_y: 15,
        max_x: 7,
        min_x: 0,
        div: undefined,
        divLegend: undefined,
        xlabel: "x",
        ylabel: "y",
        legend1: "",
        legend2: "",
        barWidth:0.3,
        toolbox_label:"Phenotype range",
        lastBin:0.0,
        ranges:undefined
    };

	var barColor = "#3071a9";
	var stroke = "#357ebd";
		
    //parse attr
    $.extend(options,attr);
    var data = options.matrix;
    var padding = 0;
    var w = d3.select(options.div).style('width').replace("px",""); 
    var h = d3.select(options.div).style('height').replace("px","");
    var scaleW = d3.scale.linear();
    var scaleH = d3.scale.linear();


// define scaling options
    scaleW.domain([options.min_x, options.max_x]);
    scaleW.range([padding, w-padding]);
    scaleH.domain([0, options.max_y+1]);
    scaleH.range([h-padding, padding]);

    var svg = d3.select(options.div)
            .append("svg")
            .attr("width", w)
            .attr("height", h);

    var aktuell = false;

 // draw graph-helplines
	var num_lines = 8;
	if ((options.max_x - options.min_x) < 8 && (options.max_x - options.min_x) > 4 ){
		var val_x = 1;
	}
	else{
		var val_x = parseFloat(((options.max_x - options.min_x)/8).toPrecision(1));
	}
	if (val_x > 1){
		par_len = 0;
	}
	else{
        var per_len = String(parseFloat(val_x.toPrecision(1))).replace(".","").length-1;
	}
	
	for (var i = 1; (i*val_x) < (options.max_x)  ; i++) {
	    if ((i*val_x) > options.min_x){
	     svg.append("svg:line")
	            .attr("x1", scaleW(val_x*i))
	            .attr("y1", scaleH(0))
	            .attr("x2", scaleW(val_x*i))
	            .attr("y2", scaleH(options.max_y+1))
	            .style("stroke", "#E6E6E6")
	            .style("stroke-width",1);
	   
		}
	};

	for (var i = 0; (i*val_x) > options.min_x  ; i--) {
	     svg.append("svg:line")
	            .attr("x1", scaleW(val_x*i))
	            .attr("y1", scaleH(0))
	            .attr("x2", scaleW(val_x*i))
	            .attr("y2", scaleH(options.max_y+1))
	            .style("stroke", "#E6E6E6")
	            .style("stroke-width",1);
	   
	};

	var val_y = Math.round(options.max_y.toPrecision(1)/5)
	for (var i = 0; (i*val_y) < (options.max_y+1); i++) {
	     svg.append("svg:line")
	            .attr("x1", scaleW(options.min_x))
	            .attr("y1", scaleH(val_y*i))
	            .attr("x2", scaleW(options.max_x)+1)
	            .attr("y2", scaleH(val_y*i))
	            .style("stroke", "#E6E6E6")
	            .style("stroke-width",1);
	  
	};

	//draw x- and y-axis
	svg.append("svg:line")
	   .attr("x1", scaleW(options.min_x))
	   .attr("y1", scaleH(0))
	   .attr("x2", scaleW(options.min_x))
	   .attr("y2", scaleH(options.max_y+1))
	   .style("stroke", "#E6E6E6")
	   .style("stroke-width",1);
	svg.append("svg:line")
	   .attr("x1", scaleW(options.min_x))
	   .attr("y1", scaleH(0))
	   .attr("x2", scaleW(options.max_x)+1)
	   .attr("y2", scaleH(0))
	   .style("stroke", "#E6E6E6")
	   .style("stroke-width",1);
	svg.append("svg:line")
	   .attr("x1", scaleW(options.min_x))
	   .attr("y1", scaleH(options.max_y+1))
	   .attr("x2", scaleW(options.max_x)+1)
	   .attr("y2", scaleH(options.max_y+1))
	   .style("stroke", "#E6E6E6")
	   .style("stroke-width",1 );
	svg.append("svg:line")
	   .attr("x1", scaleW(options.max_x)+1)
	   .attr("y1", scaleH(0))
	   .attr("x2", scaleW(options.max_x)+1)
	   .attr("y2", scaleH(options.max_y+1))
	   .style("stroke", "#E6E6E6")
	   .style("stroke-width",1 );
  // draw graph-elements
     svg.selectAll("rect")
            .data(data)
	    .enter()
	    .append("rect")
	    .attr("x", function(d){
			return (scaleW(d[0])+.5);
		})
	    .attr("y", function(d){
			return (scaleH(d[1]));
		})
	    .attr("width",function(d){
			if ((scaleW(d[0]+options.barWidth)) >= scaleW(options.max_x)+1 ){
				return Math.abs((scaleW(options.max_x)+1-scaleW(d[0]))-1);
			}
			else {
				return Math.abs(scaleW(d[0]+options.barWidth)-scaleW(d[0])-1);
			}
})
	    .attr("height", function(d){
			return (scaleH(0.1)-scaleH(d[1]))
})
            .attr("fill", barColor)
	    .attr("class", "bars")
	    .attr("stroke",stroke).attr("stroke-width","1px")
	    .attr("id", function(d){
                        return d[0];
})


					
$('#loader').remove();       
}