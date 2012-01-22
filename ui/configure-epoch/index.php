<?php
   $ENDPOINT='http://biordf.net/sparql';
   $queryT = <<<______________________________
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
               moby:objectType ?:output;
            ]
         ]
      .
   }
}
______________________________;
?>

<?php
class C9D {

   static function bind_variable($template, $variable, $binding) {
      if( strstr($binding,':') ) {
         # curie
         return str_replace($variable,' '.$binding.' ',$template);
      }else {
         # uri
         return str_replace($variable,'<'.$binding.'>',$template);
      }
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
   <link rel="stylesheet" type="text/css" media="screen" href="screen.css" />
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
      <div>
         <center>
            <a href="https://github.com/timrdf/DataFAQs/wiki">
               <img src="https://github.com/timrdf/DataFAQs/raw/master/doc/DataFAQs.png" alt="DataFAQs logo"/ width="60%"/>
            </a>
         </center>
      </div>

      <div id="epoch" class="configuration">
         <p>
            <span class="step-num">1</span> <span class="step-title">Name the epoch</span>
         </p>
         <span><?php echo date('Y-m-d')?></span>
      </div>

      <div id="select-faqts" class="faqts configuration">
         <p>
            <span class="step-num">2</span> <span class="step-title">Select evaluation services to apply</span>
         </p>
         <p class="step-description">The following SADI services will return lists of FAqT evaluation services. Choose one service and its appropriate input.
         </p>
         <?php
            $query  = C9D::bind_variable($queryT,'?:output','datafaqs:FAqTServiceCollection');
            $result = C9D::request_query($query, $ENDPOINT);

            echo '<div>';
            if( isset($result['results']['bindings']) ) {
               echo '<table about="'.$DATASET_URI.'">';
               echo "  <tr><th>select-faqts</th><th>Requires input type</th></tr>\n";
               foreach( $result['results']['bindings'] as $binding ) {
                  $service = $binding['service']['value'];
                  $input = $binding['input']['value'];
                  echo "  <tr>\n";
                  echo "     <td property='conversion:todo'><a rel='conversion:todo' href='".$service."'>".$service."</a></td>\n";
                  echo "     <td property='conversion:todo'><a rel='conversion:todo' href='".$input."'>".$input."</a></td>\n";
                  echo "  </tr>\n";
               }
               echo "</table>";
            }
            echo '</div>';

            echo '<div>';
            if( isset($result['results']['bindings']) ) {
               echo '<select>';
               foreach( $result['results']['bindings'] as $binding ) {
                  $service = $binding['service']['value'];
                  $input = $binding['input']['value'];
                  echo "  <option value='".$service."'>".$service."</option>\n";
               }
               echo "</select>";
            }
            echo '</div>';
         ?>
         with input: (new) <input type="text" name="lname" /> or previous: 
         <select>
            <option value='history 1'>history 1</option>
            <option value='history 2'>history 2</option>
            <option value='history 3'>history 3</option>
            <option value='history 4'>history 4</option>
            <option value='history 5'>history 5</option>
         </select>
      </div>

      <div id="select-datasets" class="datasets configuration">
         <p>
            <span class="step-num">3</span> <span class="step-title">Select datasets to evaluate</span>
         </p>
         <?php
            $query  = C9D::bind_variable($queryT,'?:output','datafaqs:DatasetCollection');
            $result = C9D::request_query($query, $ENDPOINT);

            echo '<div>';
            if( isset($result['results']['bindings']) ) {
               echo '<table about="'.$DATASET_URI.'">';
               echo "  <tr><th>select-datasets</th><th>Requires input type</th></tr>\n";
               foreach( $result['results']['bindings'] as $binding ) {
                  $service = $binding['service']['value'];
                  $input = $binding['input']['value'];
                  echo "  <tr>\n";
                  echo "     <td property='conversion:todo'><a rel='conversion:todo' href='".$service."'>".$service."</a></td>\n";
                  echo "     <td property='conversion:todo'><a rel='conversion:todo' href='".$input."'>".$input."</a></td>\n";
                  echo "  </tr>\n";
               }
               echo "</table>";
            }
            echo '</div>';

            echo '<div>';
            if( isset($result['results']['bindings']) ) {
               echo '<select>';
               foreach( $result['results']['bindings'] as $binding ) {
                  $service = $binding['service']['value'];
                  $input = $binding['input']['value'];
                  echo "  <option value='".$service."'>".$service."</option>\n";
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


         <div id="augment-datasets" class="datasets configuration">
            <p>
               <span class="step-num">3.1</span> 
               <input type="checkbox" name="augment-datasets" />
               <span class="step-title">Augment dataset descriptions</span>
            </p>
            <?php
               $query  = C9D::bind_variable($queryT,'?:output','datafaqs:WithReferences');
               $result = C9D::request_query($query, $ENDPOINT);

               echo '<div>';
               if( isset($result['results']['bindings']) ) {
                  echo '<table about="'.$DATASET_URI.'">';
                  echo "  <tr><th>augment-datasets</th><th>Requires input type</th></tr>\n";
                  foreach( $result['results']['bindings'] as $binding ) {
                     $service = $binding['service']['value'];
                     $input = $binding['input']['value'];
                     echo "  <tr>\n";
                     echo "     <td property='conversion:todo'><a rel='conversion:todo' href='".$service."'>".$service."</a></td>\n";
                     echo "     <td property='conversion:todo'><a rel='conversion:todo' href='".$input."'>".$input."</a></td>\n";
                     echo "  </tr>\n";
                  }
                  echo "</table>";
               }
               echo '</div>';

               echo '<div>';
               if( isset($result['results']['bindings']) ) {
                  echo '<select>';
                  foreach( $result['results']['bindings'] as $binding ) {
                     $service = $binding['service']['value'];
                     $input = $binding['input']['value'];
                     echo "  <option value='".$service."'>".$service."</option>\n";
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

      <center>
         <a href="http://test.ckan.net/"><img src="https://github.com/timrdf/DataFAQs/raw/master/doc/ckan/ckan_logo_box.png" alt="Powered by CKAN" width="80px"/></a>
         <a href="http://sadiframework.org/content/"><img src="https://github.com/timrdf/DataFAQs/raw/master/doc/sadi/sadi-header.png" alt="Powered by SADI" width="150px"/></a>
         <a href="http://code.google.com/p/surfrdf/"><img src="http://surfrdf.googlecode.com/files/surf-logo-poweredby.png" alt="Powered by SuRF" width="150px"/></a>
      </center>
   </body>                                                              
</html>
