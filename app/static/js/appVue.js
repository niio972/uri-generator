var app = new Vue({
  el: "#URI_generator",
  data: {
    URI: "your uri model",
    key_class: "primary_key",
    Details: false,
    segments: [],
    resource_type: "plant",
    supl_data: {
      year: [
        "event",
        "annotation",
        "plant",
        "plot",
        "pot",
        "leaf",
        "ear",
        "sensor",
        "vector",
        "actuator",
        "data",
        "image",
      ],
      project: ["plant", "plot", "pot", "leaf", "ear", "project"],
      relative_plant: ["leaf", "ear"],
      qrcodes: ["plot", "plant"],
    },
  },
  delimiters: ["[[", "]]"],
  methods: {
    toggleDetails: function () {
      var self = this;
      self.Details = !self.Details;
      return self.Details;
    },
    charger_csv() {
      $.ajax({
        url: "uploud",
        method: "POST",
        data: new FormData(this),
        dataType: "csv",
        contentType: false,
        processData: false,
        cache: false,
        success: function (jsonData) {
          alert("jai ete la"); //echec
          console.log("Success!");
          $("#csv_file").val("");
          $("#data-table").DataTable({
            data: jsonData,
            columns: [
              { data: "Alias" },
              { data: "Variety" },
              { data: "student_phone" },
            ],
          });
        },
      }).done(function (data) {
        alert("jai ete la"); //echec
        if (data.error) {
          $("#errorAlert").text(data.error).show();
          $("#successAlert").hide();
        } else {
          $("#successAlert").text(data.file).show();
          $("#errorAlert").hide();
        }
      });
    },
  },
  computed: {
    fill_URI: function () {
      var self = this;
      self.URI = "hostname:" + self.segments.join("/");
      return self.URI;
    },
  },
});
