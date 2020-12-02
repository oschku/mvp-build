document.addEventListener("DOMContentLoaded", function(event) {
    //do work
    document.onreadystatechange = function() {
        if (document.readyState !== "complete") {
            document.querySelector("body").style.visibility = "hidden";
            document.querySelector("#cssload-dots").style.visibility = "visible";
        } else {
            document.querySelector("#cssload-dots").style.display = "none";
            document.querySelector("body").style.visibility = "visible";
        }
    };
});

$("input[type='submit']").click(function() {
    document.addEventListener("DOMContentLoaded", function(event) {
        //do work
        document.onreadystatechange = function() {
            if (document.readyState !== "complete") {
                document.querySelector("body").style.visibility = "hidden";
                document.querySelector("#cssload-dots").style.visibility = "visible";
            } else {
                document.querySelector("#cssload-dots").style.display = "none";
                document.querySelector("body").style.visibility = "visible";
            }
        };
    });
});