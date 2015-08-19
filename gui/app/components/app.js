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
    '$http',

    function($scope, $location, $http) {
      'use strict';

       $scope.goToHome = function() {
         if ($location.path() !== '/') {
           $location.path('/');
         }
       };

      $scope.selectLibrary = function() {
        $http({
          method: 'POST',
          url: '/',
          data: {
            action: 'open_file_dialog'
          }
        }).success(function (data) {
          console.log(data);
        });
      }
    }
  ]);
