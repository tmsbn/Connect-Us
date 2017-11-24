//var width = 800, height = 800;
//
//
//var svg = d3.select("#graph").append("svg")
//        .attr("width", "100%").attr("height", "100%")
//        .attr("pointer-events", "all");
//
//var force = d3.layout.force()
//        .charge(-200).linkDistance(30).size([width, height]);
//
//
//d3.json("/graph", function(error, graph) {
//    if (error) return;
//
//    force.nodes(graph.nodes).links(graph.links).start();
//
//    var link = svg.selectAll(".link")
//            .data(graph.links).enter()
//            .append("line").attr("class", "link");
//
//    var node = svg.selectAll(".node")
//            .data(graph.nodes).enter()
//            .append("circle")
//            .attr("class", function (d) { return "node "+d.label })
//            .attr("r", 10)
//            .call(force.drag);
//
//    // html title attribute
//    node.append("title")
//            .text(function (d) { return d.title; })
//
//    // force feed algo ticks
//    force.on("tick", function() {
//        link.attr("x1", function(d) { return d.source.x; })
//                .attr("y1", function(d) { return d.source.y; })
//                .attr("x2", function(d) { return d.target.x; })
//                .attr("y2", function(d) { return d.target.y; });
//
//        node.attr("cx", function(d) { return d.x; })
//                .attr("cy", function(d) { return d.y; });
//    });
//});

$("#company_search").click(function(){

   var query=$("#company_input").val();
   alert(query);
   $.get("/searchcompany?company=" + encodeURIComponent(query),
            function (data) {
                var tbl = $("#company_results").find('tbody')
                tbl.empty()


                if (!data || data.length == 0) return;
                data.forEach(function (company) {
                    $("<tr><td>" + company.name + "</td><td>" + company.location + "</td><td>").appendTo(tbl)

                });
            }, "json");
});

$("#person_search").click(function(){

   var query=$("#person_input").val();
   alert(query);
   $.get("/searchperson?person=" + encodeURIComponent(query),
            function (data) {
                var tbl = $("#person_results").find('tbody')
                tbl.empty()
                console.log(data)

                if (!data || data.length == 0) return;
                data.forEach(function (person) {
                    $("<tr><td>" + person.name + "</td><td>" + person.position + "</td><td>").appendTo(tbl)

                });
            }, "json");
});