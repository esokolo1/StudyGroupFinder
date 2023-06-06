let item_search_template = `
<div class="field">
  <div class="control has-icons-left">
    <input class="input"
      v-bind:placeholder="'search '+item_name+'s'"
      v-model="search_query"
      @keyup="do_search" >
    <span class="icon is-left">
      <i class="fa fa-search"></i>
    </span>
  </div>
  <div class="control mb-2">
    <div style="max-height:180px;overflow:scroll;">
      <a class="panel-block"
        v-for="item in search_results"
        @click="toggle_select(item)" >
        {{item.name}}
      </a>
      <div class="panel-block has-text-grey-lighter"
        v-if="search_results.length<1" >
        no results
      </div>
    </div>
  </div>
  <div class="control buttons">
    <button class="button is-rounded has-icons-left"
      v-for="item in selected_items" >
      <span class="icon is-left is-clickable"
        @click="toggle_select(item)" >
        <i class="fa fa-remove"></i>
      </span>
      <span>{{item.name}}</span>
    </button>
    <p class="help is-danger"
      v-if="selected_items.length<min_items" >
      choose at least {{min_items}} {{item_name+(min_items==1?'':'s')}}
    </p>
  </div>
</div>
`;
let init_component = (component) => {
    component.data = function() {
      this.search_query = '';
      this.search_results = [];
    };
    component.methods = {
      do_search:function() {
        axios.get(
          this.search_url,
          {params:{query:this.search_query}},
        ).then((r) => {
          this.search_results = r.data.r;
        });
      },
      toggle_select:function(item) {
        for (let i = 0; i<this.selected_items.length; i++) {
          if (this.selected_items[i].id==item.id) {
            this.selected_items.splice(i,1);
            return;
          }
        }
        this.selected_items.push(item);
      },
    };
    component.vue = Vue.extend({
      props:[
        'item_name',
        'min_items',
        'search_url',
        'selected_items',
      ],
      data:function() { 
        this.do_search();
        return new component.data();
      },
      methods:component.methods,
      template:item_search_template,
    });
    Vue.component('item-search',component.vue);
}
let component = {};
init_component(component);
