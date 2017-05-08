declare module '*.vue' {
  import Vue from 'vue';
  export default typeof Vue;
}

declare module '*.json' {
    const value: any;
    export default value;
}
