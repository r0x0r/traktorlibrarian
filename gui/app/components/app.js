/*global $:false */
/*global angular:false */
/*global console:false */

angular.module('librarian', ['ngRoute'])

.config([
    '$routeProvider',

    function($routeProvider)  {

      $routeProvider
          .when('/clean/', {
              templateUrl: '../static/components/clean/clean.html',
              controller: 'CleanController'
          })
          .when('/export', {
              templateUrl: '../static/components/export/export.html',
              controller: 'ExportController'
          })
          .when('/', {
              templateUrl: '../static/components/landing/landing.html',
              controller: 'LandingController'
          });
    }
  ])
.controller('HeaderController', [
    '$scope',
    '$location',

    function($scope, $location) {
      'use strict';

       $scope.goToHome = function() {
         if ($location.path() !== '/') {
           $location.path('/');
         }
       };
    }
  ]);
