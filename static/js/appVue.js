var app = new Vue({
  el: '#URI_generator',
  data: {
    URI: 'your uri model',
    key_class: "random"
  },
  delimiters: ['[[',']]'],
  methods: {
    key_generator: function(key_class){
      if(key_class=="incremental")
       return "001"
      if(key_class=="random")
       return Math.floor(Math.random() * 1001);
      if(key_class=="crypto")
       return hashlib.sha224(Math.floor(Math.random() * 1001)).hexdigest()
    }
    
  }
})