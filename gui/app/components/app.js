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
    '$rootScope',
    '$route',

    function($scope, $location, $http, $rootScope, $route) {
      'use strict';

        $scope.goToHome = function() {
            $rootScope.$emit('home-event');

            if ($location.path() !== '/') {
                $location.path('/');
            }
        };

        $scope.selectLibrary = function() {
            $http({
              method: 'POST',
              url: '/choose/path',
              data: {
                traktor_check: true
              }
            }).then(function (response) {
              if(response.data.status == "ok") {
                  $rootScope.traktorDir = response.data.directory;
                  $route.reload();
              } else if (response.data.status == "error") {
                  $rootScope.$emit('error', response.data.message);
              }
            });
        }
    }
  ]);
