var app = new Vue({
  el: '#URI_generator',
  data: {
    URI: 'your uri model',
    key_class: "primary_key",
    segments: [ ]
  },
  delimiters: ['[[',']]'],
  methods:{
    GetCellValues: function() {
        var self=this
        var table = document.getElementById('mytable');
        for (var r = 1, n = table.rows.length; r < n; r++) {
            self.segments.push(table.rows[r].cells[1].innerHTML)
        }
      }
    },
  computed: {
    fill_URI: function(){
      var self=this;
      self.URI = "hostname:"+self.segments.join("/");
      return(self.URI)
    }  
    
  }
})