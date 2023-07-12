/*
A KBase module: microbial_interaction_prediction
*/

module microbial_interaction_prediction {
    typedef structure {
        string report_name;
        string report_ref;
    } ReportResults;

    /*
        This example function accepts any number of parameters and returns results in a KBaseReport
    */
    funcdef run_microbial_interaction_prediction(mapping<string,UnspecifiedObject> params) returns (ReportResults output) authentication required;

};
