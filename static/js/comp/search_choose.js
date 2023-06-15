const search_choose_tpl = `
<div class="field is-narrow">
  <div class="field mb-3">
    <p class="control buttons is-expanded">
      <button class="button has-icons-left"
        v-for="item in selected"
        :class="{'is-static': !editable}"
        @click="click(item)"
      >
        <span class="icon is-left is-clickable"
          v-show="editable"
        >
          <i class="fa fa-times"></i>
        </span>
        <span>{{display(item)}}</span>
      </button>
    </p>
  </div>
  <div class="field has-addons" v-show="editable">
    <p class="control is-expanded has-icons-left">
      <input class="input"
        placeholder="search"
        v-model="query"
        @keyup="search"
      >
      <span class="icon is-left">
        <i class="fa fa-search"></i>
      </span>
    </p>
  </div>
  <div class="field" v-show="editable"
    style="max-height: 180px; overflow: scroll;"
  >
    <a class="panel-block"
      v-for="item in list"
      @click="click(item)"
    >
      {{display(item)}}
    </a>
    <p class="panel-block has-text-grey-lighter"
      v-show="list.length < 1"
    >
      no results
    </p>
  </div>
</div>
`;
Vue.component('search-choose', {
  props: {
    search_url: String,
    selected: Array,
    click: Function,
    display: Function,
    results_name: String,
    editable: Boolean,
  },
  data: function() {
    this.search();
    return {
      query: '',
      list: '',
    };
  },
  methods: {
    search: function() {
      axios.get(this.search_url, { params: {
        query: this.query,
      }}).then((r) => {
        this.list = r.data[this.results_name];
      });
    }
  },
  template: search_choose_tpl,
});
