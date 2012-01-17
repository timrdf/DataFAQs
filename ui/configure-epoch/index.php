<?php
class C9D {

   static function bind_variable($template, $variable, $binding) {
      return str_replace($variable,'<'.$binding.'>',$template);
   }

   static function request_query($query, $endpoint) {
      return json_decode(file_get_contents(C9D::prepare_query($query, $endpoint)), true);
   }

   static function prepare_query($query, $endpoint) {
      $params           = array();
      $params["query"]  = $query;
      $params["output"] = 'sparql';
      $params["output"] = 'json';
      $query= $endpoint . '?' . http_build_query($params,'','&') ;
      return $query;
   }

   static function pretty_date($XSD_DATETIME) {
      return substr($XSD_DATETIME,0,10) . ' at ' . substr($XSD_DATETIME,11,5);
   }
}
?>

<html> 
    <head>                                                                  
    <script type="text/javascript" src="jquery-1.7.1.js"></script>          
    <script type="text/javascript">                                         

$(document).ready(function() {

   $("a").click(function() {
      alert("Hello world!");
   });

});

    </script>                                                               
    </head>                                                              
    <body>                                                               
         <center>
            <a href="https://github.com/timrdf/DataFAQs/wiki">
               <img src="https://github.com/timrdf/DataFAQs/raw/master/doc/DataFAQs.png" alt="DataFAQs logo"/ width="60%">
            </a>
         </center>
         <div>
      <span><?php echo date('Y-m-d')?></span>
         </div>
         <a href="">Link</a>
<?php
   $query = <<<______________________________
prefix moby: <http://www.mygrid.org.uk/mygrid-moby-service#>
prefix void: <http://rdfs.org/ns/void#>
prefix datafaqs: <http://purl.org/twc/vocab/datafaqs#>

select distinct ?service ?input
where {
   graph <http://sadiframework.org/registry/> {
      ?service
         moby:hasOperation [
            a moby:operation;
            moby:inputParameter [
               moby:objectType ?input;
            ];
            moby:outputParameter [
               moby:objectType datafaqs:FAqTServiceCollection;
            ]
         ]
      .
   }
}
______________________________;
   //$DATASET_URI='http://logd.tw.rpi.edu/source/data-gov/dataset/4383/version/2011-Nov-29';
   //echo $DATASET_URI;
   //$query = C9D::bind_variable($query,'?:dataset',$DATASET_URI);

   $ENDPOINT='http://biordf.net/sparql';
   // TODO: echo '<code style="display:none">'.$query.'</code>';
   $result = C9D::request_query($query, $ENDPOINT);

   echo '<div>';
   if( isset($result['results']['bindings']) ) {
      echo '<table about="'.$DATASET_URI.'">';
      echo '  <tr><th>select-faqts</th><th>Requires input type</th></tr>';
      foreach( $result['results']['bindings'] as $binding ) {
         $service = $binding['service']['value'];
         $input = $binding['input']['value'];
         echo "  <tr>";
         echo "     <td property='conversion:todo'><a rel='conversion:todo' href='".$service."'>".$service."</a></td>";
         echo "     <td property='conversion:todo'><a rel='conversion:todo' href='".$input."'>".$input."</a></td>";
         if( isset($binding['datetime']) ) {
            $date = $binding['datetime']['value'];
            echo "  <td property='conversion:todo'>".C9D::pretty_date($date)."</td>";
         }
         echo "  </tr>";
      }
      echo "</table>";
   }
   echo '</div>';

   echo '<div>';
   if( isset($result['results']['bindings']) ) {
      echo '<select>';
      echo '  <tr><th>select-faqts</th></tr>';
      foreach( $result['results']['bindings'] as $binding ) {
         $service = $binding['service']['value'];
         $input = $binding['input']['value'];
         echo "  <option value='".$service."'>".$service."</option>";
      }
      echo "</select>";
   }
   echo '</div>';
?>
with input: (new) <input type="text" name="lname" /> or previous: <select>
<option value='history 1'>history 1</option>
<option value='history 2'>history 2</option>
<option value='history 3'>history 3</option>
<option value='history 4'>history 4</option>
<option value='history 5'>history 5</option>
</select>




<div id="select-datasets">
<?php
   $query = <<<______________________________
prefix moby: <http://www.mygrid.org.uk/mygrid-moby-service#>
prefix void: <http://rdfs.org/ns/void#>
prefix datafaqs: <http://purl.org/twc/vocab/datafaqs#>

select distinct ?service ?input
where {
   graph <http://sadiframework.org/registry/> {
      ?service
         moby:hasOperation [
            a moby:operation;
            moby:inputParameter [
               moby:objectType ?input;
            ];
            moby:outputParameter [
               moby:objectType datafaqs:DatasetCollection;
            ]
         ]
      .
   }
}
______________________________;
   //$DATASET_URI='http://logd.tw.rpi.edu/source/data-gov/dataset/4383/version/2011-Nov-29';
   //echo $DATASET_URI;
   //$query = C9D::bind_variable($query,'?:dataset',$DATASET_URI);

   $ENDPOINT='http://biordf.net/sparql';
   // TODO: echo '<code style="display:none">'.$query.'</code>';
   $result = C9D::request_query($query, $ENDPOINT);

   echo '<div>';
   if( isset($result['results']['bindings']) ) {
      echo '<table about="'.$DATASET_URI.'">';
      echo '  <tr><th>select-datasets</th><th>Requires input type</th></tr>';
      foreach( $result['results']['bindings'] as $binding ) {
         $service = $binding['service']['value'];
         $input = $binding['input']['value'];
         echo "  <tr>";
         echo "     <td property='conversion:todo'><a rel='conversion:todo' href='".$service."'>".$service."</a></td>";
         echo "     <td property='conversion:todo'><a rel='conversion:todo' href='".$input."'>".$input."</a></td>";
         if( isset($binding['datetime']) ) {
            $date = $binding['datetime']['value'];
            echo "  <td property='conversion:todo'>".C9D::pretty_date($date)."</td>";
         }
         echo "  </tr>";
      }
      echo "</table>";
   }
   echo '</div>';

   echo '<div>';
   if( isset($result['results']['bindings']) ) {
      echo '<select>';
      echo '  <tr><th>select-faqts</th></tr>';
      foreach( $result['results']['bindings'] as $binding ) {
         $service = $binding['service']['value'];
         $input = $binding['input']['value'];
         echo "  <option value='".$service."'>".$service."</option>";
      }
      echo "</select>";
   }
   echo '</div>';
?>

with input: (new) <input type="text" name="lname" /> or previous: <select>
<option value='history 1'>history 1</option>
<option value='history 2'>history 2</option>
<option value='history 3'>history 3</option>
<option value='history 4'>history 4</option>
<option value='history 5'>history 5</option>
</select>


<div id="augment-datasets" class="configuration">
Augment dataset descriptions: <input type="checkbox" name="augment-datasets" />
<?php
   $query = <<<______________________________
prefix moby: <http://www.mygrid.org.uk/mygrid-moby-service#>
prefix void: <http://rdfs.org/ns/void#>
prefix datafaqs: <http://purl.org/twc/vocab/datafaqs#>

select distinct ?service ?input
where {
   graph <http://sadiframework.org/registry/> {
      ?service
         moby:hasOperation [
            a moby:operation;
            moby:inputParameter [
               moby:objectType ?input;
            ];
            moby:outputParameter [
               moby:objectType datafaqs:WithReferences;
            ]
         ]
      .
   }
}
______________________________;
   //$DATASET_URI='http://logd.tw.rpi.edu/source/data-gov/dataset/4383/version/2011-Nov-29';
   //echo $DATASET_URI;
   //$query = C9D::bind_variable($query,'?:dataset',$DATASET_URI);

   $ENDPOINT='http://biordf.net/sparql';
   // TODO: echo '<code style="display:none">'.$query.'</code>';
   $result = C9D::request_query($query, $ENDPOINT);

   echo '<div>';
   if( isset($result['results']['bindings']) ) {
      echo '<table about="'.$DATASET_URI.'">';
      echo '  <tr><th>augment-datasets</th><th>Requires input type</th></tr>';
      foreach( $result['results']['bindings'] as $binding ) {
         $service = $binding['service']['value'];
         $input = $binding['input']['value'];
         echo "  <tr>";
         echo "     <td property='conversion:todo'><a rel='conversion:todo' href='".$service."'>".$service."</a></td>";
         echo "     <td property='conversion:todo'><a rel='conversion:todo' href='".$input."'>".$input."</a></td>";
         if( isset($binding['datetime']) ) {
            $date = $binding['datetime']['value'];
            echo "  <td property='conversion:todo'>".C9D::pretty_date($date)."</td>";
         }
         echo "  </tr>";
      }
      echo "</table>";
   }
   echo '</div>';

   echo '<div>';
   if( isset($result['results']['bindings']) ) {
      echo '<select>';
      echo '  <tr><th>select-faqts</th></tr>';
      foreach( $result['results']['bindings'] as $binding ) {
         $service = $binding['service']['value'];
         $input = $binding['input']['value'];
         echo "  <option value='".$service."'>".$service."</option>";
      }
      echo "</select>";
   }
   echo '</div>';
?>
with input: (new) <input type="text" name="lname" /> or previous: <select>
<option value='history 1'>history 1</option>
<option value='history 2'>history 2</option>
<option value='history 3'>history 3</option>
<option value='history 4'>history 4</option>
<option value='history 5'>history 5</option>
</select>
</div>

</div> <!-- select-datasets -->

    </body>                                                              
</html>

