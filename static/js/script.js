// author: Kritka Sahni, Jitesh Fulwariya, Palash Kumar Koutu, Thomas Binu
// Description: JS functions to hit end-points to get data ad display it.

// Suggest companies for person
function suggestCompanies(query){

  console.log('suggest companies for:' + query)
  $.get("/suggestcompanies?person=" + encodeURIComponent(query),
            function (data) {
                var tbl = $("#company_suggestion_results").find('tbody')
                tbl.empty()

                console.log('company suggestions')
                console.log(data);
                if (!data || data.length == 0) return;
                data.forEach(function (company) {
                    $("<tr><td>" + company.name + "</td><td>" + company.openings + "</td><td>").appendTo(tbl)

                });
            }, "json");
    }

// Suggest connections for person
function suggestConnections(query){

  console.log('suggest connection for:' + query)
  $.get("/suggestconnections?person=" + encodeURIComponent(query),
            function (data) {
                var tbl = $("#connection_suggestion_results").find('tbody')
                tbl.empty()

                console.log('connection suggestions')
                console.log(data);
                if (!data || data.length == 0) return;
                data.forEach(function (connection) {
                    $("<tr><td>" + connection.name + "</td><td>" + connection.position + "</td><td>" + connection.company + "</td></tr>").appendTo(tbl)

                });
            }, "json");
    }


// Get connections of person
function getConnections(query){

  $.get("/connections?person=" + encodeURIComponent(query),
            function (data) {
                var tbl = $("#connections_results").find('tbody')
                tbl.empty()

                //console.log(data);
                if (!data || data.length == 0) return;
                data.forEach(function (connection) {
                    $("<tr><td>" + connection.name + "</td><td>" + connection.position + "</td><td>" + connection.company + "</td></tr>").appendTo(tbl)

                });
            }, "json");
}

// Search company by text
$("#company_search").click(function(){

   var query=$("#company_input").val();
   alert(query);
   $.get("/searchcompany?company=" + encodeURIComponent(query),
            function (data) {
                var tbl = $("#company_results").find('tbody')
                tbl.empty()


                if (!data || data.length == 0) return;
                data.forEach(function (company) {
                    $("<tr><td>" + company.name + "</td><td>" + company.location + "</td></tr>").appendTo(tbl)

                });
            }, "json");
});


// Search person by text
function searchPerson(query){

 $.get("/searchperson?person=" + encodeURIComponent(query),
            function (data) {
                var tbl = $("#person_results").find('tbody')
                tbl.empty()
                console.log(data)
                if (!data || data.length == 0) return;
                data.forEach(function (person) {

                    console.log(person);
                    $("<tr><td class='person clickable-row'>" + person.name + "</td><td>" + person.position + "</td><td>" + person.company + "</td></tr>")
                    .appendTo(tbl)
                    .click(function(){
                        var person = $(this).find("td.person").text();
                        console.log(person);

                        $(this).css("color", "red").siblings().css("color", "black");

                        getConnections(person);
                        suggestConnections(person);
                        suggestCompanies(person);
                    })

                });
            }, "json");
}

// Show person details when clicking on row
$("#person_search").click(function(){

   var query=$("#person_input").val();
   searchPerson(query);

});

// Show all persons initially
searchPerson('');